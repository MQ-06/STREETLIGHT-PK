# backend/routers/flutter/score.py
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from model.users import User
from utils.auth_utils import get_current_user, get_db
from ai_layers.layer5_final_score import FinalScoreCalculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/score", tags=["Score"])


@router.get("/{report_id}")
def get_report_score(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the current Final Confidence Score breakdown for a report.
    Re-runs the calculation and persists the updated result.
    """
    try:
        result = FinalScoreCalculator(db).calculate_final_score(report_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"❌ get_report_score error for report={report_id}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.post("/{report_id}/recalculate")
def recalculate_report_score(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Force a fresh Final Confidence Score recalculation for a report.
    Useful after community votes have updated the community_score.
    Persists and returns the fresh result.
    """
    try:
        result = FinalScoreCalculator(db).calculate_final_score(report_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"❌ recalculate_report_score error for report={report_id}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
