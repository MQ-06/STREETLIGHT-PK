#model.users.py
from sqlalchemy import Column, Integer, String
from db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__= "users"

    id=Column(Integer, primary_key=True, index=True)
    first_name=Column(String, nullable=False)
    last_name=Column(String, nullable=False)
    cnic= Column(String, unique=True, index=True, nullable=False)
    email=Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    reset_token = Column(String, nullable=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False)