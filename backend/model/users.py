#model.users.py
from sqlalchemy import Column, Integer, String, DateTime
from db.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class User(Base):
    __tablename__= "users"

    id=Column(Integer, primary_key=True, index=True)
    first_name=Column(String, nullable=False)
    last_name=Column(String, nullable=False)
    cnic= Column(String, unique=True, index=True, nullable=False)
    email=Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(50), nullable=False, default="citizen")
    reset_token = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    profile = relationship("UserProfile", back_populates="user", uselist=False)