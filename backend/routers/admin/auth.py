# backend/routers/admin/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from model.users import User
from model.routing_table import RoutingTable
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


def _get_officer_routing(db: Session, user_id: int) -> dict:
    """
    For dept_officer: look up routing_table to get city + department.
    Returns {"city": str|None, "department": str|None}.
    """
    row = (
        db.query(RoutingTable)
        .filter(RoutingTable.officer_id == user_id, RoutingTable.is_active == True)
        .first()
    )
    if row:
        return {"city": row.city, "department": row.department}
    return {"city": None, "department": None}


@router.post("/login")
def admin_login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    role = (db_user.role or "citizen").lower()
    if role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin dashboard role required.",
        )

    # Resolve city + department from role
    city       = None
    department = None

    if role == "dept_officer":
        routing = _get_officer_routing(db, db_user.id)
        city       = routing["city"]
        department = routing["department"]
    elif role == "city_admin":
        city = db_user.city          # stored directly on user row
    # super_admin → city=None, department=None (sees everything)

    token = create_access_token({
        "user_id":    db_user.id,
        "email":      db_user.email,
        "role":       role,
        "city":       city,
        "department": department,
        "scope":      "admin",
    })

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":         db_user.id,
            "email":      db_user.email,
            "first_name": db_user.first_name,
            "last_name":  db_user.last_name,
            "role":       role,
            "city":       city,
            "department": department,
        },
    }


@router.get("/me")
def admin_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role = (current_user.role or "citizen").lower()
    if role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Access denied.")

    city       = None
    department = None
    if role == "dept_officer":
        routing    = _get_officer_routing(db, current_user.id)
        city       = routing["city"]
        department = routing["department"]
    elif role == "city_admin":
        city = current_user.city

    return {
        "id":         current_user.id,
        "email":      current_user.email,
        "first_name": current_user.first_name,
        "last_name":  current_user.last_name,
        "role":       role,
        "city":       city,
        "department": department,
    }
