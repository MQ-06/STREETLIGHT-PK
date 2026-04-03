# backend/model/routing_table.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime, timezone


class RoutingTable(Base):
    """
    Maps (city, department) pairs to the responsible Department Officer.
    4 rows for MVP:
      lahore    + lmc  → Ahmad Raza
      lahore    + lwmc → Sara Khan
      faisalabad + fmc  → Bilal Chaudhry
      faisalabad + fwmc → Ayesha Nawaz
    """
    __tablename__ = "routing_table"

    id             = Column(Integer, primary_key=True, index=True)
    city           = Column(String(50),  nullable=False, index=True)   # "lahore" | "faisalabad"
    department     = Column(String(50),  nullable=False, index=True)   # "lmc" | "lwmc" | "fmc" | "fwmc"
    department_name = Column(String(200), nullable=False)              # human-readable full name
    officer_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active      = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    officer = relationship("User", foreign_keys=[officer_id])
