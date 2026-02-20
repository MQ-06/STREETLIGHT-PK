from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import SessionLocal
from model.users import User
from model.user_profile import UserProfile
from schema.userschema import UserCreate, SignupResponse
from utils.auth import hash_password
import logging

router = APIRouter()

# Configure logging (optional, helps debug server-side errors)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=SignupResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if CNIC already exists
        existing_user = db.query(User).filter(User.cnic == user.cnic).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="CNIC already registered")
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        new_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            cnic=user.cnic,
            email=user.email,
            hashed_password=hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "User created successfully",
            "user_id": new_user.id
        }

    except SQLAlchemyError as e:
        db.rollback()  # rollback in case of DB error
        logger.error(f"Database error during signup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    except Exception as e:
        logger.error(f"Unexpected error during signup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
