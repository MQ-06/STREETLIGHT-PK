# backend/model/field_worker_tokens.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime, timezone


class FieldWorkerToken(Base):
    """
    Single-use 72-hour tokenised links for field workers.
    Field workers need no account — they receive a WhatsApp/SMS link
    like: streetlight.pk/task/{report_id}?token={token}

    The token is a UUID4 hex string (no dashes).
    Created by Department Officers; consumed by the public after-photo endpoint.
    """
    __tablename__ = "field_worker_tokens"

    id                  = Column(Integer,     primary_key=True, index=True)
    token               = Column(String(64),  unique=True, nullable=False, index=True)  # UUID4 hex
    report_id           = Column(Integer,     ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_officer_id = Column(Integer,   ForeignKey("users.id"), nullable=False)

    expires_at          = Column(DateTime(timezone=True), nullable=False)  # created_at + 72h
    used                = Column(Boolean,     default=False, nullable=False)
    used_at             = Column(DateTime(timezone=True), nullable=True)

    # URL of the after-photo uploaded via this token
    after_photo_url     = Column(String,      nullable=True)

    # Result of 3-check AI verification (set when after-photo is processed)
    # "pending" | "passed" | "failed"
    verification_result = Column(String(20),  nullable=True)
    verification_note   = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    report          = relationship("Report", foreign_keys=[report_id])
    created_by      = relationship("User",   foreign_keys=[created_by_officer_id])
