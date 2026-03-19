from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from model.user_profile import UserProfile

logger = logging.getLogger(__name__)

_firebase_ready: bool = False
_firebase_init_attempted: bool = False


def init_firebase() -> bool:
    """
    Initialize firebase-admin once (best-effort).

    Requires GOOGLE_APPLICATION_CREDENTIALS to point to a Firebase service-account json.
    Safe to call multiple times.
    """
    global _firebase_ready, _firebase_init_attempted
    if _firebase_ready:
        return True
    if _firebase_init_attempted:
        return False
    _firebase_init_attempted = True

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        logger.warning("FCM disabled: GOOGLE_APPLICATION_CREDENTIALS not set")
        return False
    if not os.path.exists(creds_path):
        logger.warning(
            "FCM disabled: service-account file not found at "
            f"{creds_path}"
        )
        return False

    try:
        import firebase_admin  # type: ignore[import-not-found]
        from firebase_admin import credentials  # type: ignore[import-not-found]

        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(creds_path))
        _firebase_ready = True
        logger.info("✅ Firebase Admin initialized (FCM enabled)")
        return True
    except Exception as e:
        logger.warning(f"FCM disabled: firebase-admin init failed: {e}")
        _firebase_ready = False
        return False


def send_push_to_user(
    db: Session,
    *,
    user_id: int,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Best-effort send. Returns True if sent.
    """
    if not init_firebase():
        return False

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    token = (profile.fcm_token or "").strip() if profile else ""
    if not token:
        return False

    try:
        from firebase_admin import messaging  # type: ignore[import-not-found]

        msg = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            token=token,
        )
        messaging.send(msg)
        return True
    except Exception as e:
        logger.warning(f"⚠️ Push failed user={user_id}: {e}")
        return False

