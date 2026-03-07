# model/verification.py
from sqlalchemy import (
    Column, Integer, Float, DateTime, ForeignKey,
    UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime, timezone
import enum


class VerificationStatus(str, enum.Enum):
    PENDING   = "PENDING"
    COMPLETED = "COMPLETED"
    EXPIRED   = "EXPIRED"


class VoteChoice(str, enum.Enum):
    YES = "YES"
    NO  = "NO"


class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id        = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), unique=True, nullable=False)

    status = Column(
        SAEnum(VerificationStatus),
        default=VerificationStatus.PENDING,
        nullable=False,
    )

    # Configuration (stored per-request so thresholds can be tuned later)
    radius_m      = Column(Float,   default=500.0, comment="Search radius in metres")
    min_votes     = Column(Integer, default=3,     comment="Minimum votes needed to close")
    timeout_hours = Column(Integer, default=48,    comment="Hours before auto-expiry")

    # Aggregated vote results
    community_score = Column(Float,   nullable=True, comment="Final community score (0-100)")
    total_votes     = Column(Integer, default=0)
    yes_votes       = Column(Integer, default=0)
    no_votes        = Column(Integer, default=0)

    created_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    report = relationship("Report", back_populates="verification_request")
    votes  = relationship("VerificationVote", back_populates="request", cascade="all, delete")


class VerificationVote(Base):
    __tablename__ = "verification_votes"

    __table_args__ = (
        UniqueConstraint("request_id", "user_id", name="uq_vv_request_user"),
    )

    id         = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("verification_requests.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"),                 nullable=False)

    vote       = Column(SAEnum(VoteChoice), nullable=False)
    weight     = Column(Float, default=1.0,  comment="Vote weight from voter impact_score")
    distance_m = Column(Float, nullable=True, comment="Distance in metres from voter to report")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    request = relationship("VerificationRequest", back_populates="votes")
    voter   = relationship("User")
