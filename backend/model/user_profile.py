#backenmain/model/user_profile.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime, timezone

class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    location = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=True)
    total_reported = Column(Integer, default=0)
    total_solved = Column(Integer, default=0)
    impact_score = Column(Float, default=0.0)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="profile")
