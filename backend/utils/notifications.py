from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from model.notification import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        type: str,
        title: str,
        body: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        dedupe_key: Optional[str] = None,
    ) -> Optional[Notification]:
        n = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            dedupe_key=dedupe_key,
        )
        self.db.add(n)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            if dedupe_key:
                logger.info(f"🔕 Notification deduped: {dedupe_key}")
                return None
            raise

        self.db.refresh(n)
        return n

