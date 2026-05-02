# backend/model/report.py

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime, timezone, timedelta
import enum


# =========================
# ENUMS
# =========================

class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REVIEW_NEEDED = "REVIEW_NEEDED"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class KanbanStage(str, enum.Enum):
    NEW = "NEW"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_FEEDBACK = "AWAITING_FEEDBACK"
    RESOLVED = "RESOLVED"


class IssueCategory(str, enum.Enum):
    POTHOLE = "POTHOLE"
    TRASH = "TRASH"


class InteractionType(str, enum.Enum):
    SUPPORT = "SUPPORT"
    VERIFY = "VERIFY"


# =========================
# MAIN MODEL
# =========================

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SAEnum(IssueCategory), nullable=False)

    # Location
    location_address = Column(String, nullable=False)
    location_city = Column(String, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)

    # Image
    image_url = Column(String, nullable=True)

    status = Column(
        SAEnum(ReportStatus),
        default=ReportStatus.PENDING,
        nullable=False
    )

    support_count = Column(Integer, default=0)
    verify_count = Column(Integer, default=0)
    views = Column(Integer, default=0)

    confirmation_count = Column(Integer, default=0)
    best_image_url = Column(String, nullable=True)

    # =========================
    # AI RESULTS
    # =========================

    validation_score = Column(Float, nullable=True)
    validation_status = Column(String(20), nullable=True)
    validation_warnings = Column(Text, nullable=True)

    ai_confidence = Column(Float, nullable=True)
    ai_predicted_class = Column(String(50), nullable=True)
    ai_severity = Column(String(20), nullable=True)
    final_score = Column(Float, nullable=True)
    image_hash = Column(String(128), nullable=True)

    gps_verified = Column(Boolean, default=False)
    gps_has_photo_location = Column(Boolean, default=False)
    gps_distance_km = Column(Float, nullable=True)
    gps_spoofing_detected = Column(Boolean, default=False)

    # =========================
    # FRAUD
    # =========================

    is_flagged_for_spam = Column(Boolean, default=False, nullable=False)

    duplicate_of_id = Column(
        Integer,
        ForeignKey("reports.id"),
        nullable=True
    )

    # =========================
    # COMMUNITY + TRUST
    # =========================

    community_score = Column(Float, nullable=True)
    trust_score = Column(Float, nullable=True)

    combined_score = Column(Float, nullable=True)
    verification_status = Column(String(20), default="PENDING")

    # =========================
    # ADMIN ROUTING
    # =========================

    assigned_city = Column(String(50), nullable=True)
    assigned_department = Column(String(50), nullable=True)

    assigned_officer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    assigned_at = Column(DateTime(timezone=True), nullable=True)

    kanban_stage = Column(
        SAEnum(KanbanStage),
        default=KanbanStage.NEW,
        nullable=True
    )

    # =========================
    # RESOLUTION FLOW
    # =========================

    after_image_url = Column(String, nullable=True)
    after_image_uploaded_at = Column(DateTime(timezone=True), nullable=True)
    after_image_uploaded_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Citizen response
    citizen_response = Column(String(20), nullable=True)  # CONFIRMED | REJECTED | PENDING
    citizen_confirmed_at = Column(DateTime(timezone=True), nullable=True)

    # Notification tracking
    resolution_notified_at = Column(DateTime(timezone=True), nullable=True)

    # Auto resolve timer (7 days)
    auto_resolve_at = Column(DateTime(timezone=True), nullable=True)

    # Blockchain
    blockchain_resolve_tx = Column(String(100), nullable=True)
    blockchain_status = Column(String(20), nullable=True)  # PENDING | SUCCESS | FAILED

    # Final closure
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # =========================
    # TIMESTAMPS
    # =========================

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # =========================
    # RELATIONSHIPS
    # =========================

    reporter = relationship("User", foreign_keys=[user_id], backref="reports")

    assigned_officer = relationship(
        "User",
        foreign_keys=[assigned_officer_id]
    )

    interactions = relationship(
        "ReportInteraction",
        back_populates="report",
        cascade="all, delete"
    )

    duplicate_of = relationship(
        "Report",
        remote_side="Report.id",
        foreign_keys=[duplicate_of_id]
    )

    verification_request = relationship(
        "VerificationRequest",
        back_populates="report",
        uselist=False
    )

    comments = relationship(
        "Comment",
        back_populates="report",
        cascade="all, delete",
        order_by="Comment.created_at"
    )


# =========================
# INTERACTIONS
# =========================

class ReportInteraction(Base):
    __tablename__ = "report_interactions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    interaction_type = Column(
        SAEnum(InteractionType),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    report = relationship("Report", back_populates="interactions")


# =========================
# COMMENTS
# =========================

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    text = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    report = relationship("Report", back_populates="comments")
    user = relationship("User")


# =========================
# CONTRIBUTIONS
# =========================

class ReportContribution(Base):
    __tablename__ = "report_contributions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    image_url = Column(String, nullable=False)

    ai_confidence = Column(Float, nullable=True)
    ai_severity = Column(String(20), nullable=True)

    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )