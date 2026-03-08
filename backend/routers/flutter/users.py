# backend/routers/flutter/users.py
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from model.users import User
from model.user_profile import UserProfile
from utils.auth_utils import get_current_user, get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


class FcmTokenRequest(BaseModel):
    fcm_token: str


@router.post("/fcm-token")
def update_fcm_token(
    body: FcmTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Store or update the FCM device token for the authenticated user.

    The Flutter app should call this endpoint after login (and whenever
    FirebaseMessaging.instance.onTokenRefresh fires) so the backend can
    reach the user's device with push notifications.
    """
    try:
        profile = (
            db.query(UserProfile)
            .filter(UserProfile.user_id == current_user.id)
            .first()
        )
        if profile is None:
            raise HTTPException(status_code=404, detail="User profile not found")

        profile.fcm_token = body.fcm_token.strip()
        db.commit()

        logger.info(f"🔔 FCM token updated for user ID={current_user.id}")
        return {"success": True, "message": "FCM token updated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ update_fcm_token error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
