"""
Engine E: Final Confidence Score Calculator (Layer 5)

Reads ai_confidence, community_score, and trust_score from an existing Report
row, applies the weighted formula, and persists combined_score +
verification_status back to the same row.

BLOCKCHAIN INTEGRATION:
After score calculation, if status is AUTO_VERIFIED or REVIEW_NEEDED,
the complaint is automatically recorded on the StreetLight smart contract.
"""
#layer5_final_score/score_calculator.py
import logging
from typing import Dict, Optional

from sqlalchemy.orm import Session
from blockchain.blockchain_service import blockchain_service
from model.report import Report, ReportStatus

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

    def __init__(self, db: Session) -> None:
        self.db = db
        logger.info("🎯 FinalScoreCalculator ready")

    def calculate_final_score(self, report_id: int) -> Dict:
        logger.info("=" * 60)
        logger.info(f"🎯 LAYER 5: Calculating final score for report_id={report_id}")
        logger.info("=" * 60)

        report: Optional[Report] = (
            self.db.query(Report).filter(Report.id == report_id).first()
        )
        if report is None:
            raise ValueError(f"Report ID={report_id} not found")

        ai_score: float = (report.final_score or report.ai_confidence or 0.0)
        community_score: Optional[float] = report.community_score
        trust_score: float = report.trust_score or 0.0

        if community_score is None:
            weights_mode = "NO_COMMUNITY"
            ai_contribution        = ai_score * WEIGHT_AI_NO_COMMUNITY
            community_contribution = 0.0
            trust_contribution     = trust_score * WEIGHT_TRUST_NO_COMMUNITY
        else:
            weights_mode = "NORMAL"
            ai_contribution        = ai_score * WEIGHT_AI
            community_contribution = community_score * WEIGHT_COMMUNITY
            trust_contribution     = trust_score * WEIGHT_TRUST

        combined_score = round(
            ai_contribution + community_contribution + trust_contribution, 2
        )

        if combined_score >= THRESHOLD_AUTO_VERIFY:
            verification_status = STATUS_AUTO_VERIFIED
        elif combined_score >= THRESHOLD_REVIEW:
            verification_status = STATUS_REVIEW_NEEDED
        else:
            verification_status = STATUS_REJECTED

        if verification_status == STATUS_AUTO_VERIFIED:
            report.status = ReportStatus.VERIFIED
        elif verification_status == STATUS_REVIEW_NEEDED:
            if report.status not in (ReportStatus.RESOLVED, ReportStatus.IN_PROGRESS):
                report.status = ReportStatus.REVIEW_NEEDED
        else:
            pass

        report.combined_score      = combined_score
        report.verification_status = verification_status
        self.db.commit()

        community_label = (
            f"{community_score:.1f}" if community_score is not None else "N/A"
        )
        logger.info(
            f"   📥 Inputs — AI: {ai_score:.1f} | "
            f"Community: {community_label} | Trust: {trust_score:.1f}"
        )
        logger.info(f"   ⚖️  Mode: {weights_mode}")
        logger.info(
            f"   📊 Contributions — AI: {ai_contribution:.2f} | "
            f"Community: {community_contribution:.2f} | "
            f"Trust: {trust_contribution:.2f}"
        )
        status_emoji = (
            "✅" if verification_status == STATUS_AUTO_VERIFIED
            else "🔍" if verification_status == STATUS_REVIEW_NEEDED
            else "❌"
        )
        logger.info(
            f"   {status_emoji} combined_score={combined_score:.2f} → {verification_status}"
        )

        # ── BLOCKCHAIN INTEGRATION ────────────────────────────────────────────
        # AUTO_VERIFIED  → ComplaintVerified event (full AI confidence)
        # REVIEW_NEEDED  → ComplaintVerified event (fallback mode / officer review)
        # REJECTED       → no blockchain entry
        blockchain_result = None

        if verification_status in (STATUS_AUTO_VERIFIED, STATUS_REVIEW_NEEDED):
            blockchain_result = self._record_on_blockchain(
                report=report,
                ai_score=ai_score,
                final_score=combined_score,
                verification_status=verification_status,
            )

        return {
            "combined_score":       combined_score,
            "verification_status":  verification_status,
            "ai_score_used":        ai_score,
            "community_score_used": community_score,
            "trust_score_used":     trust_score,
            "weights_mode":         weights_mode,
            "breakdown": {
                "ai_contribution":        round(ai_contribution, 2),
                "community_contribution": round(community_contribution, 2),
                "trust_contribution":     round(trust_contribution, 2),
            },
            "blockchain": blockchain_result,
        }

    def record_officer_approval(self, report_id: int) -> Dict:
        report: Optional[Report] = (
            self.db.query(Report).filter(Report.id == report_id).first()
        )
        if report is None:
            raise ValueError(f"Report ID={report_id} not found")

        report.status = ReportStatus.VERIFIED
        report.verification_status = "OFFICER_APPROVED"
        self.db.commit()

        logger.info(f"👮 Officer approved report #{report_id} — recording on blockchain")

        return self._record_on_blockchain(
            report=report,
            ai_score=report.ai_confidence or 0.0,
            final_score=report.combined_score or 0.0,
            verification_status="OFFICER_APPROVED",
        )

    def _record_on_blockchain(
        self,
        report: Report,
        ai_score: float,
        final_score: float,
        verification_status: str,
    ) -> Dict:
        try:
            from blockchain.blockchain_service import blockchain_service

            result = blockchain_service.register_complaint(
                complaint_id        = report.id,
                image_url           = report.image_url or "",
                category            = report.category.value if report.category else "OTHER",
                latitude            = report.location_lat,
                longitude           = report.location_lng,
                verification_status = verification_status,
                ai_score            = ai_score,
                final_score         = final_score,
            )

            if result.get("success"):
                logger.info(
                    f"⛓️  Blockchain Event #1 (ComplaintVerified) — report #{report.id} | "
                    f"TX: {result.get('tx_hash', 'N/A')}"
                )
            else:
                logger.warning(
                    f"⚠️  Blockchain record FAILED for report #{report.id}: "
                    f"{result.get('error', 'Unknown error')}"
                )

            return result

        except Exception as e:
            logger.error(f"Blockchain integration error for report #{report.id}: {e}")
            return {
                "success": False,
                "error":   str(e),
                "skipped": True,
            }