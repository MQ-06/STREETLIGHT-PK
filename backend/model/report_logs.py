# backend/model/report_logs.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime, timezone


class ReportLog(Base):
    """
    Immutable audit trail for every status/stage transition on a report.
    Written by:
      - Routing service   (changed_by = "agent",   ai_managed = True)
      - Agentic AI loop   (changed_by = "agent",   ai_managed = True)
      - Officer action    (changed_by = officer_id, ai_managed = False)
      - System (auto)     (changed_by = "system",  ai_managed = True)

    Never updated or deleted — append-only.
    """
    __tablename__ = "report_logs"

    id              = Column(Integer, primary_key=True, index=True)
    report_id       = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)

    # Who caused this change — "agent" | "system" | str(officer_user_id)
    changed_by      = Column(String(100), nullable=False)

    # Stage transitions (kanban_stage values)
    previous_stage  = Column(String(50), nullable=True)
    new_stage       = Column(String(50), nullable=True)

    # Status transitions (ReportStatus values)
    previous_status = Column(String(50), nullable=True)
    new_status      = Column(String(50), nullable=True)

    # Routing metadata (set when agent routes the report)
    assigned_city        = Column(String(50),  nullable=True)
    assigned_department  = Column(String(50),  nullable=True)
    assigned_officer_id  = Column(Integer, ForeignKey("users.id"), nullable=True)

    note            = Column(Text,    nullable=True)   # human or AI-generated note
    ai_managed      = Column(Boolean, default=False,   nullable=False)  # True = agentic action

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships (read-only helpers — never cascade writes through these)
    report           = relationship("Report", foreign_keys=[report_id])
    assigned_officer = relationship("User",   foreign_keys=[assigned_officer_id])
