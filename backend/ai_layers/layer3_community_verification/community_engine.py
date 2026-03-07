"""
Engine C: Community Verification (Layer 3)

Runs AFTER a report has been persisted to the database.
Finds nearby users, collects weighted votes, and produces a Community
Confidence Score (0-100).  Community verification is optional — reports
proceed to the feed regardless of vote outcome.

Score formula:   (sum_of_yes_weights / sum_of_all_weights) * 100
Weight formula:  max(1.0, 1.0 + impact_score / 100.0)
"""

import math
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from model.report import Report
from model.user_profile import UserProfile
from model.verification import (
    VerificationRequest,
    VerificationVote,
    VerificationStatus,
    VoteChoice,
)

logger = logging.getLogger(__name__)

# ── Thresholds ─────────────────────────────────────────────────────────────
DEFAULT_RADIUS_M: float = 500.0     # Metres — radius for nearby user search
MIN_VOTES: int = 3                  # Votes needed to auto-finalise a request
TIMEOUT_HOURS: int = 48             # Hours before an unresolved request expires
BOUNDING_BOX_DEG: float = 0.005    # ±0.005° ≈ ±555 m — coarse SQL pre-filter
MIN_WEIGHT: float = 1.0            # Floor weight guaranteed to every voter


# ── CommunityVerificationEngine ─────────────────────────────────────────────

class CommunityVerificationEngine:
    """
    Layer 3: Community Verification Engine.

    Accepts the active DB session and manages the complete lifecycle of a
    VerificationRequest — creation, vote submission, score calculation, and
    timeout expiry.

    Instantiate once per operation — do NOT share across requests.

    Usage:
        engine  = CommunityVerificationEngine(db)
        request = engine.create_verification_request(report_id, lat, lng)
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        logger.info("🏘️ CommunityVerificationEngine ready")

    # ── Public API ──────────────────────────────────────────────────────────

    def create_verification_request(
        self,
        report_id: int,
        lat: float,
        lng: float,
    ) -> VerificationRequest:
        """
        Create a VerificationRequest for the given report and log nearby users.

        Finds users within DEFAULT_RADIUS_M metres using a bounding-box SQL
        pre-filter followed by precise Haversine on UserProfile.last_known_lat/lng.
        The report author is excluded from the candidate set.

        Args:
            report_id: ID of the newly persisted report.
            lat:       Report GPS latitude.
            lng:       Report GPS longitude.

        Returns:
            The persisted VerificationRequest instance.
        """
        logger.info("=" * 60)
        logger.info("🏘️ LAYER 3: Creating community verification request")
        logger.info(f"   Report ID: {report_id} | GPS: ({lat:.6f}, {lng:.6f})")
        logger.info("=" * 60)

        # Resolve report author so they are excluded from voter candidates
        report: Optional[Report] = (
            self.db.query(Report).filter(Report.id == report_id).first()
        )
        author_id: Optional[int] = report.user_id if report else None

        request = VerificationRequest(
            report_id=report_id,
            status=VerificationStatus.PENDING,
            radius_m=DEFAULT_RADIUS_M,
            min_votes=MIN_VOTES,
            timeout_hours=TIMEOUT_HOURS,
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)

        # Find nearby users (informational — push notifications handled by caller)
        nearby = self._find_nearby_users(lat, lng, DEFAULT_RADIUS_M, exclude_user_id=author_id)
        logger.info(
            f"   ✅ VerificationRequest ID={request.id} created | "
            f"{len(nearby)} nearby user(s) within {DEFAULT_RADIUS_M:.0f} m"
        )

        return request

    def submit_vote(
        self,
        request_id: int,
        user_id: int,
        vote: VoteChoice,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
    ) -> Dict:
        """
        Record a community vote on a VerificationRequest.

        Validates that the request is still PENDING and the user has not already
        voted.  Calculates vote weight from the voter's impact_score.  If the
        minimum vote threshold is met after this vote, auto-finalises the score.

        Args:
            request_id: ID of the target VerificationRequest.
            user_id:    Voting user's ID.
            vote:       VoteChoice.YES or VoteChoice.NO.
            user_lat:   Voter's current GPS latitude (optional, used for distance).
            user_lng:   Voter's current GPS longitude (optional).

        Returns:
            {
                'vote_id':         int            — Persisted vote record ID
                'weight':          float          — Applied vote weight
                'distance_m':      Optional[float]— Distance voter ↔ report in metres
                'total_votes':     int            — Running total after this vote
                'min_votes':       int            — Threshold to auto-finalise
                'score_finalised': bool           — True if auto-finalised now
                'community_score': Optional[float]— Score if finalised, else None
            }

        Raises:
            ValueError: If request not found, not PENDING, or user already voted.
        """
        logger.info(
            f"🗳️  Layer 3 — submit_vote: request={request_id} "
            f"user={user_id} vote={vote.value}"
        )

        request: Optional[VerificationRequest] = (
            self.db.query(VerificationRequest)
            .filter(VerificationRequest.id == request_id)
            .first()
        )

        if request is None:
            raise ValueError(f"VerificationRequest ID={request_id} not found")

        if request.status != VerificationStatus.PENDING:
            raise ValueError(
                f"VerificationRequest ID={request_id} is {request.status.value} — voting closed"
            )

        # Guard: one vote per user per request (also enforced by DB UniqueConstraint)
        existing_vote: Optional[VerificationVote] = (
            self.db.query(VerificationVote)
            .filter(
                VerificationVote.request_id == request_id,
                VerificationVote.user_id == user_id,
            )
            .first()
        )
        if existing_vote is not None:
            raise ValueError(
                f"User ID={user_id} has already voted on request ID={request_id}"
            )

        # Vote weight: floor at MIN_WEIGHT, grows linearly with impact_score
        profile: Optional[UserProfile] = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )
        impact_score: float = profile.impact_score if profile else 0.0
        weight: float = max(MIN_WEIGHT, MIN_WEIGHT + impact_score / 100.0)

        # Distance from voter to report location (both sets of coords must be present)
        distance_m: Optional[float] = None
        report: Optional[Report] = (
            self.db.query(Report).filter(Report.id == request.report_id).first()
        )
        if (
            user_lat is not None
            and user_lng is not None
            and report is not None
            and report.location_lat is not None
            and report.location_lng is not None
        ):
            distance_m = round(
                self._haversine_km(
                    user_lat, user_lng,
                    report.location_lat, report.location_lng,
                ) * 1_000.0,
                1,
            )

        # Persist the vote
        new_vote = VerificationVote(
            request_id=request_id,
            user_id=user_id,
            vote=vote,
            weight=round(weight, 4),
            distance_m=distance_m,
        )
        self.db.add(new_vote)

        # Update request counters
        request.total_votes += 1
        if vote == VoteChoice.YES:
            request.yes_votes += 1
        else:
            request.no_votes += 1

        self.db.commit()
        self.db.refresh(new_vote)
        self.db.refresh(request)

        dist_label = f"{distance_m:.1f} m" if distance_m is not None else "N/A"
        logger.info(
            f"   ✅ Vote recorded: ID={new_vote.id} | weight={weight:.3f} | "
            f"distance={dist_label} | "
            f"totals: {request.total_votes}/{request.min_votes} required"
        )

        # Auto-finalise when vote threshold is reached
        score_finalised = False
        if request.total_votes >= request.min_votes:
            logger.info(
                f"   🏁 Threshold reached ({request.total_votes} votes) — auto-finalising score"
            )
            self._calculate_community_score(request_id)
            self.db.refresh(request)
            score_finalised = True

        return {
            "vote_id": new_vote.id,
            "weight": round(weight, 4),
            "distance_m": distance_m,
            "total_votes": request.total_votes,
            "min_votes": request.min_votes,
            "score_finalised": score_finalised,
            "community_score": request.community_score,
        }

    def get_verification_status(self, report_id: int) -> Optional[Dict]:
        """
        Return the current verification state for a report.

        Args:
            report_id: ID of the report to look up.

        Returns:
            Dict with full status, vote counts, score, and individual vote list.
            None if no VerificationRequest exists for this report.
        """
        request: Optional[VerificationRequest] = (
            self.db.query(VerificationRequest)
            .filter(VerificationRequest.report_id == report_id)
            .first()
        )

        if request is None:
            return None

        return {
            "request_id": request.id,
            "status": request.status.value,
            "total_votes": request.total_votes,
            "yes_votes": request.yes_votes,
            "no_votes": request.no_votes,
            "min_votes": request.min_votes,
            "community_score": request.community_score,
            "created_at": request.created_at.isoformat(),
            "completed_at": (
                request.completed_at.isoformat() if request.completed_at else None
            ),
            "votes": [
                {
                    "vote_id": v.id,
                    "user_id": v.user_id,
                    "vote": v.vote.value,
                    "weight": v.weight,
                    "distance_m": v.distance_m,
                    "created_at": v.created_at.isoformat(),
                }
                for v in request.votes
            ],
        }

    def finalize_expired_requests(self) -> int:
        """
        Scan all PENDING requests whose timeout has elapsed and expire them.

        For each timed-out request:
          • ≥1 vote:  calculate score from partial votes → status EXPIRED (score preserved)
          • 0 votes:  community_score = NULL            → status EXPIRED

        Also propagates community_score to the linked Report row.

        Returns:
            Number of requests transitioned to EXPIRED in this run.
        """
        logger.info("⏳ Layer 3 — finalize_expired_requests: scanning for timed-out requests")

        now = datetime.now(timezone.utc)
        expired_count = 0

        pending_requests: List[VerificationRequest] = (
            self.db.query(VerificationRequest)
            .filter(VerificationRequest.status == VerificationStatus.PENDING)
            .all()
        )

        for request in pending_requests:
            # Attach UTC timezone info if the stored timestamp is naïve
            created_utc = (
                request.created_at
                if request.created_at.tzinfo is not None
                else request.created_at.replace(tzinfo=timezone.utc)
            )
            deadline = created_utc + timedelta(hours=request.timeout_hours)

            if now < deadline:
                continue  # Not yet expired

            logger.info(
                f"   ⏰ Request ID={request.id} (report {request.report_id}) expired — "
                f"{request.total_votes} vote(s) collected"
            )

            if request.total_votes > 0:
                # Partial score from whatever votes were collected
                self._calculate_community_score(request.id)
                self.db.refresh(request)
            else:
                # Zero votes — propagate NULL to Report
                report: Optional[Report] = (
                    self.db.query(Report)
                    .filter(Report.id == request.report_id)
                    .first()
                )
                if report is not None:
                    report.community_score = None
                request.community_score = None

            # Override to EXPIRED regardless (COMPLETED only for threshold-triggered closes)
            request.status = VerificationStatus.EXPIRED
            if request.completed_at is None:
                request.completed_at = now

            self.db.commit()
            expired_count += 1

            logger.info(
                f"   ✅ Expired: request ID={request.id} | "
                f"community_score={request.community_score}"
            )

        logger.info(
            f"   🏁 finalize_expired_requests complete — {expired_count} request(s) expired"
        )
        return expired_count

    # ── Private helpers ─────────────────────────────────────────────────────

    def _calculate_community_score(self, request_id: int) -> None:
        """
        Compute the weighted community score and persist the result.

        Formula: (sum_of_yes_weights / sum_of_all_weights) * 100

        Mutations:
          • VerificationRequest.community_score  ← computed score (0-100)
          • VerificationRequest.status           ← COMPLETED
          • VerificationRequest.completed_at     ← now (UTC)
          • Report.community_score               ← mirrors the same value

        If votes list is unexpectedly empty, score is set to NULL and the
        request is still marked COMPLETED so it isn't processed again.
        """
        votes: List[VerificationVote] = (
            self.db.query(VerificationVote)
            .filter(VerificationVote.request_id == request_id)
            .all()
        )

        request: Optional[VerificationRequest] = (
            self.db.query(VerificationRequest)
            .filter(VerificationRequest.id == request_id)
            .first()
        )

        if request is None:
            logger.error(f"_calculate_community_score: request ID={request_id} not found")
            return

        now = datetime.now(timezone.utc)

        if not votes:
            logger.info(
                f"   _calculate_community_score: no votes for request ID={request_id} — score=NULL"
            )
            request.community_score = None
            request.status = VerificationStatus.COMPLETED
            request.completed_at = now
            self.db.commit()
            return

        sum_all_weights: float = sum(v.weight for v in votes)
        sum_yes_weights: float = sum(v.weight for v in votes if v.vote == VoteChoice.YES)
        score: float = (sum_yes_weights / sum_all_weights) * 100.0

        request.community_score = round(score, 2)
        request.status = VerificationStatus.COMPLETED
        request.completed_at = now

        # Mirror score to the Report row
        report: Optional[Report] = (
            self.db.query(Report).filter(Report.id == request.report_id).first()
        )
        if report is not None:
            report.community_score = round(score, 2)

        self.db.commit()

        logger.info(
            f"   📊 Score: {score:.2f} | "
            f"YES weight: {sum_yes_weights:.2f} / total weight: {sum_all_weights:.2f} | "
            f"{len(votes)} vote(s)"
        )

    def _find_nearby_users(
        self,
        lat: float,
        lng: float,
        radius_m: float,
        exclude_user_id: Optional[int] = None,
    ) -> List[Tuple[int, float]]:
        """
        Return (user_id, distance_m) tuples for users within radius_m metres.

        Two-phase strategy (mirrors Layer 2 duplicate detection):
          Phase 1: Coarse bounding-box SQL filter on UserProfile.last_known_lat/lng
          Phase 2: Precise Haversine check in Python on the small candidate set

        Users without a recorded last-known location are skipped automatically.

        Args:
            lat:             Centre latitude of the report.
            lng:             Centre longitude of the report.
            radius_m:        Search radius in metres.
            exclude_user_id: User to exclude (report author).

        Returns:
            List of (user_id, distance_m), sorted nearest-first.
        """
        radius_km = radius_m / 1_000.0

        # Phase 1: coarse bounding-box SQL filter
        query = self.db.query(UserProfile).filter(
            UserProfile.last_known_lat.isnot(None),
            UserProfile.last_known_lng.isnot(None),
            UserProfile.last_known_lat.between(lat - BOUNDING_BOX_DEG, lat + BOUNDING_BOX_DEG),
            UserProfile.last_known_lng.between(lng - BOUNDING_BOX_DEG, lng + BOUNDING_BOX_DEG),
        )
        if exclude_user_id is not None:
            query = query.filter(UserProfile.user_id != exclude_user_id)

        candidates: List[UserProfile] = query.all()

        logger.info(
            f"   _find_nearby_users: bounding-box (±{BOUNDING_BOX_DEG}°) "
            f"returned {len(candidates)} candidate(s)"
        )

        # Phase 2: precise Haversine filter
        nearby: List[Tuple[int, float]] = []
        for profile in candidates:
            dist_km = self._haversine_km(
                lat, lng,
                profile.last_known_lat,
                profile.last_known_lng,
            )
            dist_m = dist_km * 1_000.0
            if dist_km <= radius_km:
                nearby.append((profile.user_id, round(dist_m, 1)))

        nearby.sort(key=lambda pair: pair[1])  # nearest first
        return nearby

    def _haversine_km(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Return the great-circle distance in kilometres between two GPS coordinates.

        Uses the Haversine formula, accurate to within ~0.3% for terrestrial distances.
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
