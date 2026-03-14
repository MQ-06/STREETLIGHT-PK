"""
Blockchain Router
FastAPI endpoints for blockchain operations.

Endpoints:
    GET  /blockchain/health              — Check blockchain connection
    GET  /blockchain/complaint/{id}      — Get complaint proof (Flutter uses this)
    GET  /blockchain/stats               — Total/resolved/pending stats
    POST /blockchain/resolve/{id}        — Mark complaint resolved (municipal admin)
"""
#routers/blockchain.py
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from blockchain.blockchain_service import blockchain_service
from db.database import get_db
from model.report import Report

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/blockchain",
    tags=["Blockchain"],
)


# ── Request/Response Models ───────────────────────────────────────────────────

class ResolveRequest(BaseModel):
    resolution_note: str = "Issue resolved by municipality"


class BlockchainProofResponse(BaseModel):
    success: bool
    complaint_id: int
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    image_hash: Optional[str] = None
    issue_category: Optional[str] = None
    verified_at: Optional[int] = None
    resolved_at: Optional[int] = None
    verification_type: Optional[str] = None
    status: Optional[str] = None
    ai_score: Optional[int] = None
    final_score: Optional[int] = None
    exists: Optional[bool] = None
    error: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/health")
def blockchain_health():
    """
    Check if blockchain connection is alive.
    Flutter can poll this to show blockchain status in UI.
    """
    is_healthy = blockchain_service.is_healthy()

    return {
        "status":   "connected" if is_healthy else "disconnected",
        "enabled":  blockchain_service.enabled,
        "healthy":  is_healthy,
        "message":  (
            "Blockchain operational" if is_healthy
            else "Blockchain disabled or unreachable"
        ),
    }


@router.get("/complaint/{complaint_id}", response_model=BlockchainProofResponse)
def get_complaint_proof(complaint_id: int):
    """
    Get blockchain proof for a complaint.
    
    Flutter calls this to show user their immutable proof:
    - Image hash (tamper detection)
    - Verification type (auto/officer)
    - AI score and final score
    - Blockchain timestamp
    
    Public endpoint — no auth needed (blockchain data is public).
    """
    result = blockchain_service.get_complaint_proof(complaint_id)

    if not result.get("success") and not result.get("skipped"):
        raise HTTPException(
            status_code=404,
            detail=f"Complaint #{complaint_id} not found on blockchain"
        )

    return BlockchainProofResponse(
        success      = result.get("success", False),
        complaint_id = complaint_id,
        **{k: v for k, v in result.items() if k not in ("success", "complaint_id")}
    )


@router.get("/stats")
def get_blockchain_stats():
    """
    Get overall stats from the smart contract.
    Municipal admin dashboard uses this.
    """
    result = blockchain_service.get_stats()

    if not result.get("success"):
        return {
            "success": False,
            "total":   0,
            "resolved": 0,
            "pending": 0,
            "error": result.get("error", "Blockchain unavailable"),
        }

    return result


@router.post("/resolve/{complaint_id}")
def mark_complaint_resolved(
    complaint_id: int,
    request: ResolveRequest,
    db: Session = Depends(get_db),
):
    """
    Mark a complaint as resolved on blockchain.
    
    Called by municipal admin when they fix the issue.
    This triggers Blockchain Event #2 (ComplaintResolved).
    
    Also updates the DB report status to RESOLVED.
    """
    # ── Verify report exists in DB ────────────────────────────────────────────
    report = db.query(Report).filter(Report.id == complaint_id).first()
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report #{complaint_id} not found in database"
        )

    # ── Check it's verified first ─────────────────────────────────────────────
    if report.verification_status not in ("AUTO_VERIFIED", "OFFICER_APPROVED"):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Report #{complaint_id} is not verified yet "
                f"(status: {report.verification_status}). "
                f"Only verified complaints can be resolved."
            )
        )

    # ── Call blockchain ───────────────────────────────────────────────────────
    result = blockchain_service.mark_resolved(
        complaint_id    = complaint_id,
        resolution_note = request.resolution_note,
    )

    # ── Update DB status ──────────────────────────────────────────────────────
    if result.get("success"):
        from model.report import ReportStatus
        report.status = ReportStatus.RESOLVED
        db.commit()
        logger.info(f"✅ Report #{complaint_id} marked RESOLVED in DB + blockchain")

    return {
        "success":          result.get("success", False),
        "complaint_id":     complaint_id,
        "tx_hash":          result.get("tx_hash"),
        "block_number":     result.get("block_number"),
        "resolution_note":  request.resolution_note,
        "error":            result.get("error"),
    }