#routers/forget_password.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from model.users import User
from schema.userschema import ForgetPasswordRequest
import secrets

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/forget-password")
def forget_password(request: ForgetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    token = secrets.token_urlsafe(16)
    user.reset_token = token
    db.commit()
    db.refresh(user)
    
    return {"message": "Reset token generated", "reset_token": token}
