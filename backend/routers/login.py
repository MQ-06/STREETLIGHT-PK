#routers/login.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from model.users import User
from schema.userschema import UserLogin
from utils.auth import verify_password, create_access_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"user_id": db_user.id, "email": db_user.email})
    return {"access_token": token, "token_type": "bearer",
             "user": {
                    "id": db_user.id,
                    "email": db_user.email,
                    "first_name": db_user.first_name,
                    "last_name": db_user.last_name,
                }
            }
