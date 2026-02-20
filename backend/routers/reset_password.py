#routers/reset-password.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from model.users import User
from schema.userschema import ResetPasswordRequest
from utils.auth import hash_password

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == request.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    user.hashed_password = hash_password(request.new_password)
    user.reset_token = None
    db.commit()
    db.refresh(user)
    
    return {"message": "Password updated successfully"}
