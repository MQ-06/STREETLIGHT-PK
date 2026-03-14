"""
Engine E: Final Confidence Score Calculator (Layer 5)

Reads ai_confidence, community_score, and trust_score from an existing Report
row, applies the weighted formula, and persists combined_score +
verification_status back to the same row.
"""

import logging
from typing import Dict, Optional

from sqlalchemy.orm import Session

from model.report import Report

logger = logging.getLogger(__name__)

# ── Weights ───────────────────────────────────────────────────────────────────
WEIGHT_AI: float = 0.40
WEIGHT_COMMUNITY: float = 0.30
WEIGHT_TRUST: float = 0.30

WEIGHT_AI_NO_COMMUNITY: float = 0.55
WEIGHT_TRUST_NO_COMMUNITY: float = 0.45

# ── Decision thresholds ───────────────────────────────────────────────────────
THRESHOLD_AUTO_VERIFY: float = 85.0
THRESHOLD_REVIEW: float = 60.0

# ── Status labels ─────────────────────────────────────────────────────────────
STATUS_AUTO_VERIFIED: str = "VERIFIED"
STATUS_REVIEW_NEEDED: str = "REVIEW_NEEDED"
STATUS_REJECTED: str = "REJECTED"


class FinalScoreCalculator:
    """
    Layer 5: Final Confidence Score Calculator.

    Accepts the active DB session and computes a combined_score for a single
    report, then persists the result.

    Instantiate once per operation — do NOT share across requests.

    Usage:
        result = FinalScoreCalculator(db).calculate_final_score(report_id)
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        logger.info("🎯 FinalScoreCalculator ready")

    # ── Public API ────────────────────────────────────────────────────────────

    def calculate_final_score(self, report_id: int) -> Dict:
        """
        Compute the combined confidence score for a report and persist it.

        Reads ai_confidence, community_score, and trust_score from the Report
        row.  If community_score is None (no votes yet), the two-factor weights
        are used so the result is still meaningful.

        Args:
            report_id: ID of the target Report row.

        Returns:
            {
                'combined_score':        float       — Weighted final score (0-100)
                'verification_status':   str         — AUTO_VERIFIED | REVIEW_NEEDED | REJECTED
                'ai_score_used':         float       — AI confidence value used
                'community_score_used':  float|None  — Community score value used (None if absent)
                'trust_score_used':      float       — Trust score value used
                'weights_mode':          str         — "NORMAL" or "NO_COMMUNITY"
                'breakdown': {
                    'ai_contribution':          float
                    'community_contribution':   float  (0 when NO_COMMUNITY mode)
                    'trust_contribution':       float
                }
            }

        Raises:
            ValueError: If the report does not exist.
        """
        logger.info("=" * 60)
        logger.info(f"🎯 LAYER 5: Calculating final confidence score for report_id={report_id}")
        logger.info("=" * 60)

        report: Optional[Report] = (
            self.db.query(Report).filter(Report.id == report_id).first()
        )
        if report is None:
            raise ValueError(f"Report ID={report_id} not found")

        # ── Collect raw scores ────────────────────────────────────────────────
        ai_score: float = report.ai_confidence or 0.0
        community_score: Optional[float] = report.community_score   # may be None
        trust_score: float = report.trust_score or 0.0

        # ── Apply weights ─────────────────────────────────────────────────────
        if community_score is None:
            weights_mode = "NO_COMMUNITY"
            ai_contribution = ai_score * WEIGHT_AI_NO_COMMUNITY
            community_contribution = 0.0
            trust_contribution = trust_score * WEIGHT_TRUST_NO_COMMUNITY
        else:
            weights_mode = "NORMAL"
            ai_contribution = ai_score * WEIGHT_AI
            community_contribution = community_score * WEIGHT_COMMUNITY
            trust_contribution = trust_score * WEIGHT_TRUST

        combined_score = round(
            ai_contribution + community_contribution + trust_contribution, 2
        )

        # ── Determine status ──────────────────────────────────────────────────
        if combined_score >= THRESHOLD_AUTO_VERIFY:
            verification_status = STATUS_AUTO_VERIFIED
        elif combined_score >= THRESHOLD_REVIEW:
            verification_status = STATUS_REVIEW_NEEDED
        else:
            verification_status = STATUS_REJECTED

        # ── Persist ───────────────────────────────────────────────────────────
        report.combined_score = combined_score
        report.verification_status = verification_status
        self.db.commit()

        # ── Log breakdown ─────────────────────────────────────────────────────
        community_label = f"{community_score:.1f}" if community_score is not None else "N/A"
        logger.info(
            f"   📥 Inputs — AI: {ai_score:.1f} | "
            f"Community: {community_label} | Trust: {trust_score:.1f}"
        )
        logger.info(f"   ⚖️  Mode: {weights_mode}")
        logger.info(
            f"   📊 Contributions — AI: {ai_contribution:.2f} | "
            f"Community: {community_contribution:.2f} | Trust: {trust_contribution:.2f}"
        )

        status_emoji = (
            "✅" if verification_status == STATUS_AUTO_VERIFIED
            else "🔍" if verification_status == STATUS_REVIEW_NEEDED
            else "❌"
        )
        logger.info(
            f"   {status_emoji} combined_score={combined_score:.2f} → {verification_status}"
        )

        return {
            "combined_score": combined_score,
            "verification_status": verification_status,
            "ai_score_used": ai_score,
            "community_score_used": community_score,
            "trust_score_used": trust_score,
            "weights_mode": weights_mode,
            "breakdown": {
                "ai_contribution": round(ai_contribution, 2),
                "community_contribution": round(community_contribution, 2),
                "trust_contribution": round(trust_contribution, 2),
            },
        }
