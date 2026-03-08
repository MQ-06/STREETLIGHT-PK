from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from model.users import User
from schema.userschema import UserLogin
from utils.auth import verify_password, create_access_token
from utils.auth_utils import get_current_user
from utils.rbac import ADMIN_ROLES

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login")
def admin_login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_role = (db_user.role or "citizen").lower()
    if user_role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin dashboard role required.",
        )

    token = create_access_token({
        "user_id": db_user.id,
        "email": db_user.email,
        "role": db_user.role,
        "scope": "admin",
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "role": db_user.role,
        },
    }


@router.get("/me")
def admin_me(current_user: User = Depends(get_current_user)):
    user_role = (current_user.role or "citizen").lower()
    if user_role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin dashboard role required.",
        )

    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
    }
