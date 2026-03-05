"""
Engine B: Fraud Detection (Layer 2)

Runs AFTER Layer 1 AI Classification and BEFORE Cloudinary upload.
Performs three sequential, database-driven fraud checks using SQLAlchemy/Postgres.
No paid external APIs are used — all logic is pure Python + SQL.

Checks (in priority order):
    1. Impossible Travel  → HARD BLOCK  (GPS spoofing)
    2. Duplicate Report   → HARD BLOCK  (same category, ≤30 m, last 14 days)
    3. Spam Pattern       → SOFT FLAG   (>20 reports in last 1 hour)
"""

import math
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session

from model.report import IssueCategory, Report

logger = logging.getLogger(__name__)

# ── Thresholds ─────────────────────────────────────────────────────────────
IMPOSSIBLE_TRAVEL_KM: float = 100.0    # Distance that is physically impossible in < 2 min
IMPOSSIBLE_TRAVEL_MIN: float = 2.0     # Time window (minutes) for travel check

DUPLICATE_RADIUS_M: float = 30.0       # Radius (metres) for duplicate detection
DUPLICATE_WINDOW_DAYS: int = 14        # Look-back window (days) for duplicate search
BOUNDING_BOX_DEG: float = 0.001        # ±0.001° ≈ ±111 m — coarse SQL pre-filter

SPAM_WINDOW_HOURS: int = 1             # Rolling window for spam count
SPAM_THRESHOLD: int = 20               # Max reports per window before soft-flagging


# ── Haversine helper ────────────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Return the great-circle distance in kilometres between two GPS coordinates.

    Uses the Haversine formula, accurate to within ~0.3 % for terrestrial distances.
    """
    R = 6_371.0  # Earth mean radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def _ensure_utc(dt: datetime) -> datetime:
    """Attach UTC timezone info if the datetime is naïve."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


# ── FraudDetector ───────────────────────────────────────────────────────────

class FraudDetector:
    """
    Layer 2: Fraud Detection Engine.

    Accepts the active DB session and report metadata; executes three checks.
    Instantiate once per request — do NOT share across requests.

    Usage:
        detector = FraudDetector(db)
        result   = detector.run_all_checks(user_id, category, lat, lng, submitted_at)
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        logger.info("🛡️ FraudDetector ready")

    # ── Public API ─────────────────────────────────────────────────────────

    def run_all_checks(
        self,
        user_id: int,
        category: IssueCategory,
        lat: float,
        lng: float,
        submitted_at: datetime,
    ) -> Dict:
        """
        Execute all three fraud checks in priority order and return a unified result dict.

        Args:
            user_id:      ID of the submitting user.
            category:     AI-detected issue category (IssueCategory enum).
            lat:          Submitted GPS latitude.
            lng:          Submitted GPS longitude.
            submitted_at: UTC datetime at the moment of submission.

        Returns:
            {
                'is_spoofed':       bool           — Check 1 result (HARD BLOCK if True)
                'duplicate_of_id':  Optional[int]  — Check 2: ID of original report
                'duplicate_report': Optional[dict] — Check 2: serialised original report
                'is_spam':          bool           — Check 3 result (SOFT FLAG if True)
                'hourly_count':     int            — Reports submitted by user in last hour
            }
        """
        submitted_at = _ensure_utc(submitted_at)

        logger.info("=" * 60)
        logger.info("🛡️ LAYER 2: Fraud Detection — starting checks")
        logger.info(
            f"   User: {user_id} | GPS: ({lat:.6f}, {lng:.6f}) | Category: {category.value}"
        )
        logger.info("=" * 60)

        result: Dict = {
            "is_spoofed": False,
            "duplicate_of_id": None,
            "duplicate_report": None,
            "is_spam": False,
            "hourly_count": 0,
        }

        # ── Check 1 ────────────────────────────────────────────────────────
        result["is_spoofed"] = self._check_impossible_travel(
            user_id, lat, lng, submitted_at
        )
        if result["is_spoofed"]:
            logger.warning("🚨 Layer 2 verdict: GPS SPOOFING — hard block")
            logger.info("=" * 60)
            return result  # Short-circuit: no further checks needed

        # ── Check 2 ────────────────────────────────────────────────────────
        dup_id, dup_report = self._check_duplicate(category, lat, lng, submitted_at)
        result["duplicate_of_id"] = dup_id
        result["duplicate_report"] = dup_report
        if dup_id is not None:
            logger.warning(f"📋 Layer 2 verdict: DUPLICATE of report ID={dup_id} — hard block")
            logger.info("=" * 60)
            return result  # Short-circuit

        # ── Check 3 ────────────────────────────────────────────────────────
        is_spam, hourly_count = self._check_spam(user_id, submitted_at)
        result["is_spam"] = is_spam
        result["hourly_count"] = hourly_count

        if is_spam:
            logger.warning(
                f"⚠️ Layer 2 verdict: SPAM FLAG — {hourly_count} reports in last hour "
                f"(soft flag; report will be saved for admin review)"
            )
        else:
            logger.info(
                f"✅ Layer 2 verdict: CLEAN — passed all fraud checks "
                f"(hourly count: {hourly_count})"
            )

        logger.info("=" * 60)
        return result

    # ── Check 1: Impossible Travel / GPS Spoofing ──────────────────────────

    def _check_impossible_travel(
        self,
        user_id: int,
        lat: float,
        lng: float,
        submitted_at: datetime,
    ) -> bool:
        """
        Compare the incoming GPS position against the user's most recent report.

        A jump of more than IMPOSSIBLE_TRAVEL_KM km within IMPOSSIBLE_TRAVEL_MIN
        minutes is physically impossible and indicates GPS spoofing.

        Returns:
            True  → spoofing detected  (HARD BLOCK)
            False → plausible location (OK)
        """
        logger.info("🔍 Check 1 — Impossible Travel / GPS Spoofing...")

        last_report: Optional[Report] = (
            self.db.query(Report)
            .filter(Report.user_id == user_id)
            .order_by(Report.created_at.desc())
            .first()
        )

        if (
            last_report is None
            or last_report.location_lat is None
            or last_report.location_lng is None
        ):
            logger.info("   ✓ No previous geo-tagged report — spoofing check skipped")
            return False

        distance_km = _haversine_km(
            last_report.location_lat, last_report.location_lng, lat, lng
        )

        last_ts = _ensure_utc(last_report.created_at)
        delta_min = (submitted_at - last_ts).total_seconds() / 60.0

        logger.info(
            f"   Previous report: ({last_report.location_lat:.6f}, {last_report.location_lng:.6f})"
            f" | ID={last_report.id} | {last_ts.isoformat()}"
        )
        logger.info(
            f"   Distance: {distance_km:.2f} km | Time delta: {delta_min:.2f} min"
        )

        if distance_km > IMPOSSIBLE_TRAVEL_KM and delta_min < IMPOSSIBLE_TRAVEL_MIN:
            logger.warning(
                f"   🚨 Impossible jump: {distance_km:.1f} km in {delta_min:.1f} min — SPOOFED"
            )
            return True

        logger.info("   ✓ Travel distance / time are plausible — check passed")
        return False

    # ── Check 2: Duplicate Report ──────────────────────────────────────────

    def _check_duplicate(
        self,
        category: IssueCategory,
        lat: float,
        lng: float,
        submitted_at: datetime,
    ) -> Tuple[Optional[int], Optional[Dict]]:
        """
        Detect whether an identical civic issue already exists nearby.

        Strategy — two-phase for efficiency:
          Phase 1: Coarse SQL bounding-box filter (fast index scan, ±BOUNDING_BOX_DEG)
          Phase 2: Precise Haversine check in Python on the small candidate set

        A report is a duplicate if:
          • Same IssueCategory
          • Submitted within the last DUPLICATE_WINDOW_DAYS days
          • Located within DUPLICATE_RADIUS_M metres of the new submission

        Returns:
            (id, serialised_dict) of the original report if a duplicate is found.
            (None, None) otherwise.
        """
        logger.info("🔍 Check 2 — Duplicate Report Detection...")

        window_start = submitted_at - timedelta(days=DUPLICATE_WINDOW_DAYS)
        radius_km = DUPLICATE_RADIUS_M / 1_000.0

        # Phase 1: coarse bounding-box SQL filter
        candidates = (
            self.db.query(Report)
            .filter(
                Report.category == category,
                Report.created_at >= window_start,
                Report.location_lat.isnot(None),
                Report.location_lng.isnot(None),
                Report.location_lat.between(lat - BOUNDING_BOX_DEG, lat + BOUNDING_BOX_DEG),
                Report.location_lng.between(lng - BOUNDING_BOX_DEG, lng + BOUNDING_BOX_DEG),
            )
            .order_by(Report.created_at.asc())   # oldest first → prefer the true original
            .all()
        )

        logger.info(
            f"   Bounding-box candidates ({BOUNDING_BOX_DEG}°, last {DUPLICATE_WINDOW_DAYS}d): "
            f"{len(candidates)} report(s)"
        )

        # Phase 2: precise Haversine filter
        for report in candidates:
            dist_km = _haversine_km(
                report.location_lat, report.location_lng, lat, lng
            )
            dist_m = dist_km * 1_000.0
            if dist_km <= radius_km:
                logger.warning(
                    f"   📋 Duplicate hit: Report ID={report.id} | "
                    f"Distance: {dist_m:.1f} m | Category: {category.value}"
                )
                dup_dict = {
                    "id": report.id,
                    "title": report.title,
                    "location_address": report.location_address,
                    "status": report.status.value,
                    "created_at": report.created_at.isoformat(),
                    "distance_m": round(dist_m, 1),
                }
                return report.id, dup_dict

            logger.info(
                f"   Candidate ID={report.id} at {dist_m:.1f} m — outside {DUPLICATE_RADIUS_M} m radius"
            )

        logger.info(f"   ✓ No duplicate found within {DUPLICATE_RADIUS_M} m — check passed")
        return None, None

    # ── Check 3: Spam Pattern ──────────────────────────────────────────────

    def _check_spam(
        self,
        user_id: int,
        submitted_at: datetime,
    ) -> Tuple[bool, int]:
        """
        Count the user's accepted reports within the last SPAM_WINDOW_HOURS hour(s).

        If the count exceeds SPAM_THRESHOLD the report is soft-flagged — it is still
        uploaded to Cloudinary and saved to the database, but is_flagged_for_spam is
        set to True so admins can review it.

        Returns:
            (is_spam, hourly_count)
        """
        logger.info("🔍 Check 3 — Spam Pattern Detection...")

        window_start = submitted_at - timedelta(hours=SPAM_WINDOW_HOURS)

        hourly_count: int = (
            self.db.query(Report)
            .filter(
                Report.user_id == user_id,
                Report.created_at >= window_start,
            )
            .count()
        )

        is_spam = hourly_count > SPAM_THRESHOLD

        logger.info(
            f"   Reports in last {SPAM_WINDOW_HOURS}h: {hourly_count} "
            f"(threshold: >{SPAM_THRESHOLD}) → {'⚠️ SPAM FLAG' if is_spam else '✓ OK'}"
        )

        return is_spam, hourly_count
