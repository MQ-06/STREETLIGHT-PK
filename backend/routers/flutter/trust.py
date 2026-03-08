# backend/routers/flutter/trust.py
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from model.users import User
from utils.auth_utils import get_current_user, get_db
from ai_layers.layer4_trust_history import TrustHistoryEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trust", tags=["Trust"])


@router.get("/my-score")
def get_my_trust_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the Trust Score breakdown for the currently authenticated user.
    """
    try:
        trust_result = TrustHistoryEngine(db).evaluate_trust(current_user.id)
        return {"success": True, "data": trust_result}
    except Exception as e:
        logger.error(f"❌ get_my_trust_score error for user={current_user.id}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/{user_id}/score")
def get_user_trust_score(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the Trust Score breakdown for any user by ID.
    Requires authentication.
    """
    try:
        trust_result = TrustHistoryEngine(db).evaluate_trust(user_id)
        return {"success": True, "data": trust_result}
    except Exception as e:
        logger.error(f"❌ get_user_trust_score error for user={user_id}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
