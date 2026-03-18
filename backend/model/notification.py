from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    type = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)

    # Optional linkage for deep-linking/navigation
    entity_type = Column(String(50), nullable=True, index=True)
    entity_id = Column(Integer, nullable=True, index=True)

    # Optional payload (kept small). Stored as JSON/JSONB on Postgres.
    data = Column(JSON, nullable=True)

    # Prevent duplicate notifications for the same event.
    dedupe_key = Column(String(200), nullable=True, unique=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    read_at = Column(DateTime(timezone=True), nullable=True, index=True)

    user = relationship("User")

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    def mark_read(self) -> None:
        if self.read_at is None:
            self.read_at = datetime.now(timezone.utc)

