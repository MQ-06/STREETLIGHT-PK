from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime, timezone
import enum


class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class IssueCategory(str, enum.Enum):
    POTHOLE = "POTHOLE"
    TRASH = "TRASH"

class InteractionType(str, enum.Enum):
    SUPPORT = "SUPPORT"
    VERIFY = "VERIFY"


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

    # Image stored as Cloudinary URL
    image_url = Column(String, nullable=True)

    status = Column(SAEnum(ReportStatus), default=ReportStatus.PENDING)

    support_count = Column(Integer, default=0)
    verify_count = Column(Integer, default=0)
    views = Column(Integer, default=0)

    # ==========================================
    # AI AGENT RESULTS (NEW)
    # ==========================================
    
    # Layer 0: Validation Results
    validation_score = Column(Float, nullable=True, comment="Image quality score (0-100)")
    validation_status = Column(String(20), nullable=True, comment="passed or failed")
    validation_warnings = Column(Text, nullable=True, comment="JSON array of warnings")
    
    # Layer 1: AI Classification Results
    ai_confidence = Column(Float, nullable=True, comment="AI confidence score (0-100)")
    ai_predicted_class = Column(String(50), nullable=True, comment="pothole or garbage")
    ai_severity = Column(String(20), nullable=True, comment="small, medium, or large")
    final_score = Column(Float, nullable=True, comment="Combined AI + GPS score (0-100)")
    
    # GPS Verification Results
    gps_verified = Column(Boolean, default=False, comment="Location verified with landmarks")
    gps_has_photo_location = Column(Boolean, default=False, comment="Photo contained GPS in EXIF")
    gps_distance_km = Column(Float, nullable=True, comment="Distance between photo & submitted GPS")
    gps_spoofing_detected = Column(Boolean, default=False, comment="Large GPS mismatch detected")

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    reporter = relationship("User", backref="reports")
    interactions = relationship(
        "ReportInteraction",
        back_populates="report",
        cascade="all, delete"
    )


class ReportInteraction(Base):
    __tablename__ = "report_interactions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interaction_type = Column(SAEnum(InteractionType), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    report = relationship("Report", back_populates="interactions")