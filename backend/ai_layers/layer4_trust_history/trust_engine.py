"""
Engine D: Trust History (Layer 4)

Produces a weighted Trust Score (0-100) from four independent sub-scores:

  Sub-score              Weight  Driver
  ─────────────────────  ──────  ──────────────────────────────────────────────
  Account Age Score       20 %   Days since User.created_at  (30 d → 100)
  Report History Score    30 %   UserProfile.total_reported   (10+ → 100)
  Fraud History Score     30 %   UserProfile.fraud_flags      (each flag −25)
  Behaviour Score         20 %   Reports in last 1 h          (≥5 → suspicious)

Final formula:
    trust_score = (age * 0.20) + (history * 0.30) + (fraud * 0.30) + (behaviour * 0.20)
    is_trusted  = trust_score >= 40
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Optional

from sqlalchemy.orm import Session

from model.users import User
from model.user_profile import UserProfile
from model.report import Report

logger = logging.getLogger(__name__)

# ── Thresholds & weights ──────────────────────────────────────────────────────
TRUST_THRESHOLD: float = 40.0          # Minimum score to be considered trusted

AGE_WEIGHT: float = 0.20
HISTORY_WEIGHT: float = 0.30
FRAUD_WEIGHT: float = 0.30
BEHAVIOR_WEIGHT: float = 0.20

AGE_FULL_DAYS: int = 30               # Days of account age for a full age score
HISTORY_FULL_REPORTS: int = 10        # Reports needed for a full history score
HISTORY_BASELINE: float = 30.0        # Baseline given to brand-new users
FRAUD_PENALTY_PER_FLAG: float = 25.0  # Points deducted per fraud flag
BEHAVIOR_BURST_THRESHOLD: int = 5     # Reports/hour considered a suspicious burst
BEHAVIOR_BURST_SCORE: float = 20.0    # Score assigned during a burst
BEHAVIOR_NORMAL_SCORE: float = 80.0   # Score assigned for normal activity


# ── TrustHistoryEngine ────────────────────────────────────────────────────────

class TrustHistoryEngine:
    """
    Layer 4: Trust History Engine.

    Accepts the active DB session and evaluates a single user's trustworthiness.

    Instantiate once per operation — do NOT share across requests.

    Usage:
        result = TrustHistoryEngine(db).evaluate_trust(user_id)
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        logger.info("🔐 TrustHistoryEngine ready")

    # ── Public API ────────────────────────────────────────────────────────────

    def evaluate_trust(self, user_id: int) -> Dict:
        """
        Run all four sub-score calculations and return the combined Trust Score.

        Args:
            user_id: The user to evaluate.

        Returns:
            {
                'trust_score':          float   — Weighted final score (0-100)
                'is_trusted':           bool    — True if trust_score >= 40
                'account_age_days':     int     — Days since account creation
                'account_age_score':    float   — Sub-score (0-100)
                'report_history_score': float   — Sub-score (0-100)
                'fraud_history_score':  float   — Sub-score (0-100)
                'behavior_score':       float   — Sub-score (0-100)
                'fraud_flags':          int     — Raw fraud flag count
                'total_reports':        int     — Raw lifetime report count
            }
        """
        logger.info("=" * 60)
        logger.info(f"🔐 LAYER 4: Evaluating trust for user_id={user_id}")
        logger.info("=" * 60)

        age_score, age_days = self._calculate_account_age_score(user_id)
        history_score, total_reports = self._calculate_report_history_score(user_id)
        fraud_score, fraud_flags = self._calculate_fraud_history_score(user_id)
        behavior_score = self._calculate_behavior_score(user_id)

        trust_score = round(
            (age_score * AGE_WEIGHT)
            + (history_score * HISTORY_WEIGHT)
            + (fraud_score * FRAUD_WEIGHT)
            + (behavior_score * BEHAVIOR_WEIGHT),
            2,
        )
        is_trusted = trust_score >= TRUST_THRESHOLD

        logger.info(
            f"   📊 Sub-scores — age: {age_score:.1f} ({age_days}d) | "
            f"history: {history_score:.1f} ({total_reports} reports) | "
            f"fraud: {fraud_score:.1f} ({fraud_flags} flags) | "
            f"behaviour: {behavior_score:.1f}"
        )
        logger.info(
            f"   {'✅' if is_trusted else '⚠️ '} Trust Score: {trust_score:.2f} / 100 "
            f"| is_trusted={is_trusted}"
        )

        return {
            "trust_score": trust_score,
            "is_trusted": is_trusted,
            "account_age_days": age_days,
            "account_age_score": age_score,
            "report_history_score": history_score,
            "fraud_history_score": fraud_score,
            "behavior_score": behavior_score,
            "fraud_flags": fraud_flags,
            "total_reports": total_reports,
        }

    # ── Private sub-score calculators ─────────────────────────────────────────

    def _calculate_account_age_score(self, user_id: int) -> Tuple[float, int]:
        """
        Score based on days since User.created_at.

        Formula: min(100, (age_days / 30) * 100)
        0 days → 0, 30+ days → 100, linear in between.

        Returns:
            (score, age_days)
        """
        user: Optional[User] = (
            self.db.query(User).filter(User.id == user_id).first()
        )

        if user is None or user.created_at is None:
            logger.warning(
                f"   _calculate_account_age_score: user_id={user_id} not found "
                "or has no created_at — defaulting to 0"
            )
            return 0.0, 0

        # Normalise to UTC-aware datetime if stored as naïve
        created_utc = (
            user.created_at
            if user.created_at.tzinfo is not None
            else user.created_at.replace(tzinfo=timezone.utc)
        )
        age_days = (datetime.now(timezone.utc) - created_utc).days
        score = min(100.0, (age_days / AGE_FULL_DAYS) * 100.0)
        return round(score, 2), age_days

    def _calculate_report_history_score(self, user_id: int) -> Tuple[float, int]:
        """
        Score based on UserProfile.total_reported.

        Formula: min(100, 30 + (total_reported / 10) * 70)
        0 reports → 30 (baseline trust), 10+ reports → 100, linear in between.

        Returns:
            (score, total_reported)
        """
        profile: Optional[UserProfile] = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        total_reported = profile.total_reported if profile else 0
        total_reported = total_reported or 0

        score = min(
            100.0,
            HISTORY_BASELINE + (total_reported / HISTORY_FULL_REPORTS) * (100.0 - HISTORY_BASELINE),
        )
        return round(score, 2), total_reported

    def _calculate_fraud_history_score(self, user_id: int) -> Tuple[float, int]:
        """
        Score based on UserProfile.fraud_flags.

        Formula: max(0, 100 - (fraud_flags * 25))
        0 flags → 100, 1 flag → 75, 2 flags → 50, 4+ flags → 0.

        Returns:
            (score, fraud_flags)
        """
        profile: Optional[UserProfile] = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        fraud_flags = profile.fraud_flags if profile else 0
        fraud_flags = fraud_flags or 0

        score = max(0.0, 100.0 - (fraud_flags * FRAUD_PENALTY_PER_FLAG))
        return round(score, 2), fraud_flags

    def _calculate_behavior_score(self, user_id: int) -> float:
        """
        Score based on reports submitted by this user in the last 1 hour.

        If the user has submitted 5+ reports within the past hour the pattern
        is treated as suspicious and a low score (20) is returned; otherwise
        normal score (80) is returned.

        Returns:
            score (float)
        """
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        recent_count: int = (
            self.db.query(Report)
            .filter(
                Report.user_id == user_id,
                Report.created_at >= one_hour_ago,
            )
            .count()
        )

        if recent_count >= BEHAVIOR_BURST_THRESHOLD:
            logger.warning(
                f"   _calculate_behavior_score: user_id={user_id} submitted "
                f"{recent_count} reports in the last hour (burst detected)"
            )
            return BEHAVIOR_BURST_SCORE

        return BEHAVIOR_NORMAL_SCORE
