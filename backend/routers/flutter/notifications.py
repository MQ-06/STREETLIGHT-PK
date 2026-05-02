#routers/flutter/notification.py
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from model.notification import Notification
from model.users import User
from utils.auth_utils import get_current_user, get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    body: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    created_at: str
    read_at: Optional[str] = None


class MarkReadRequest(BaseModel):
    read: bool = True


def _serialize(n: Notification) -> Dict[str, Any]:
    return {
        "id": n.id,
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "entity_type": n.entity_type,
        "entity_id": n.entity_id,
        "data": n.data,
        "created_at": n.created_at.isoformat() if n.created_at else None,
        "read_at": n.read_at.isoformat() if n.read_at else None,
    }


@router.get("")
def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[int] = Query(None, description="Return items with id < cursor (pagination)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(Notification).filter(Notification.user_id == current_user.id)
        if unread_only:
            q = q.filter(Notification.read_at.is_(None))
        if cursor is not None:
            q = q.filter(Notification.id < cursor)

        items: List[Notification] = (
            q.order_by(Notification.id.desc())
            .limit(limit)
            .all()
        )
        next_cursor = items[-1].id if len(items) == limit else None

        return {
            "success": True,
            "count": len(items),
            "next_cursor": next_cursor,
            "notifications": [_serialize(n) for n in items],
        }
    except Exception as e:
        logger.error(f"❌ list_notifications error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Server error")


@router.get("/unread-count")
def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        count = (
            db.query(Notification)
            .filter(Notification.user_id == current_user.id, Notification.read_at.is_(None))
            .count()
        )
        return {"success": True, "unread_count": count}
    except Exception as e:
        logger.error(f"❌ unread_count error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Server error")


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    body: MarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        n: Optional[Notification] = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
            .first()
        )
        if n is None:
            raise HTTPException(status_code=404, detail="Notification not found")

        if body.read:
            if n.read_at is None:
                n.read_at = datetime.now(timezone.utc)
        else:
            n.read_at = None

        db.commit()
        db.refresh(n)
        return {"success": True, "notification": _serialize(n)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ mark_read error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Server error")

