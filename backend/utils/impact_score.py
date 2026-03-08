# backend/utils/impact_score.py
"""
Centralized impact score and fraud flag manager.

All engines and routers must use ImpactScoreManager instead of touching
UserProfile.impact_score or UserProfile.fraud_flags directly.
"""
import logging
from sqlalchemy.orm import Session

from model.user_profile import UserProfile

logger = logging.getLogger(__name__)

# ── Point constants ───────────────────────────────────────────────────────────
POINTS_REPORT_CREATED: int = 10   # Report passes all fraud checks
POINTS_VOTE_CAST: int = 5         # Community verification vote cast
POINTS_REPORT_RESOLVED: int = 20  # User's report gets marked resolved

PENALTY_SPOOFING: int = 50        # GPS spoofing detected
PENALTY_SPAM: int = 30            # Spam pattern detected
PENALTY_DUPLICATE: int = 10       # Duplicate report submitted

# Reason substrings that indicate a fraud-related deduction
_FRAUD_KEYWORDS = ("SPOOF", "SPAM", "DUPLICATE")


class ImpactScoreManager:
    """
    Manages UserProfile.impact_score and UserProfile.fraud_flags.

    Instantiate per-request with the active DB session.

    Usage:
        mgr = ImpactScoreManager(db)
        mgr.award_points(user_id, POINTS_REPORT_CREATED, "REPORT_CREATED")
        mgr.deduct_points(user_id, PENALTY_SPOOFING, "GPS_SPOOFING")
        score = mgr.get_score(user_id)
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Public API ────────────────────────────────────────────────────────────

    def award_points(self, user_id: int, points: int, reason: str) -> None:
        """
        Add `points` to the user's impact_score.

        Args:
            user_id: Target user ID.
            points:  Positive integer to add.
            reason:  Human-readable label logged alongside the change.
        """
        profile = self._get_profile(user_id)
        if profile is None:
            logger.warning(f"⚠️  award_points: no profile for user_id={user_id} — skipped")
            return

        before = profile.impact_score or 0.0
        profile.impact_score = before + points
        self.db.commit()

        logger.info(
            f"📈 +{points} pts → user={user_id} | reason={reason} | "
            f"score: {before:.1f} → {profile.impact_score:.1f}"
        )

    def deduct_points(self, user_id: int, points: int, reason: str) -> None:
        """
        Subtract `points` from the user's impact_score.

        If `reason` contains any of SPOOF / SPAM / DUPLICATE (case-insensitive),
        UserProfile.fraud_flags is also incremented by 1.

        Args:
            user_id: Target user ID.
            points:  Positive integer to subtract.
            reason:  Human-readable label; drives fraud_flags increment.
        """
        profile = self._get_profile(user_id)
        if profile is None:
            logger.warning(f"⚠️  deduct_points: no profile for user_id={user_id} — skipped")
            return

        before = profile.impact_score or 0.0
        profile.impact_score = before - points

        is_fraud = any(kw in reason.upper() for kw in _FRAUD_KEYWORDS)
        if is_fraud:
            profile.fraud_flags = (profile.fraud_flags or 0) + 1

        self.db.commit()

        flag_note = f" | fraud_flags={profile.fraud_flags}" if is_fraud else ""
        logger.warning(
            f"📉 -{points} pts → user={user_id} | reason={reason} | "
            f"score: {before:.1f} → {profile.impact_score:.1f}{flag_note}"
        )

    def get_score(self, user_id: int) -> float:
        """
        Return the current impact_score for the user, or 0.0 if not found.

        Args:
            user_id: Target user ID.

        Returns:
            Current impact_score as a float.
        """
        profile = self._get_profile(user_id)
        if profile is None:
            return 0.0
        return profile.impact_score or 0.0

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_profile(self, user_id: int):
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )
