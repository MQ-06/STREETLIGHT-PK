from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
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