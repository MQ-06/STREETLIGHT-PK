# backend/routers/admin/users.py
"""
Admin user management endpoints.

Role visibility:
  super_admin  → all admin users
  city_admin   → dept_officer users in their city only
  dept_officer → themselves only

Create/update restricted to super_admin.
"""
import logging
import random
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from db.database import SessionLocal
from model.routing_table import RoutingTable
from model.users import User
from utils.auth import hash_password
from utils.auth_utils import get_current_user
from utils.rbac import require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])

ALL_ADMIN = require_roles(
    "super_admin", "city_admin", "dept_officer",
    "municipal_officer", "department_head", "city_planner", "system_admin",
)
SA_ONLY   = require_roles("super_admin")
SA_OR_CA  = require_roles("super_admin", "city_admin")

ADMIN_ROLES = {"super_admin", "city_admin", "dept_officer"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _user_dict(u: User, db: Session) -> dict:
    routing = None
    if (u.role or "").lower() == "dept_officer":
        routing = (
            db.query(RoutingTable)
            .filter_by(officer_id=u.id, is_active=True)
            .first()
        )
    return {
        "id":                 u.id,
        "first_name":         u.first_name,
        "last_name":          u.last_name,
        "email":              u.email,
        "role":               u.role,
        "city":               u.city,
        "department":         routing.department if routing else None,
        "dept_name":          routing.department_name if routing else None,
        "notification_email": u.notification_email,
        "is_active":          True,
        "created_at":         u.created_at.isoformat() if u.created_at else None,
    }


# ── GET /admin/users ────────────────────────────────────────────────────────

@router.get("")
def list_users(
    current_user: User = Depends(ALL_ADMIN),
    db: Session           = Depends(get_db),
):
    role = (current_user.role or "").lower()
    q = db.query(User).filter(User.role.in_(list(ADMIN_ROLES)))

    if role == "city_admin" and current_user.city:
        q = q.filter(User.city == current_user.city, User.role == "dept_officer")
    elif role == "dept_officer":
        q = q.filter(User.id == current_user.id)

    users = q.order_by(User.role, User.first_name).all()
    return {"users": [_user_dict(u, db) for u in users], "total": len(users)}


# ── POST /admin/users ───────────────────────────────────────────────────────

class CreateUserBody(BaseModel):
    first_name:         str
    last_name:          str
    email:              str
    password:           str
    role:               str          # city_admin | dept_officer
    city:               Optional[str] = None
    department:         Optional[str] = None
    dept_name:          Optional[str] = None
    notification_email: Optional[str] = None


@router.post("")
def create_user(
    body:         CreateUserBody,
    current_user: User    = Depends(SA_OR_CA),
    db:           Session = Depends(get_db),
):
    caller_role = (current_user.role or "").lower()

    # city_admin can only create dept_officer accounts for their own city
    if caller_role == "city_admin":
        if body.role != "dept_officer":
            raise HTTPException(403, "City admins may only create dept_officer accounts")
        if body.city and body.city.lower() != (current_user.city or "").lower():
            raise HTTPException(403, "City admins may only create accounts for their own city")
        # Force city to caller's city
        body = CreateUserBody(**{**body.dict(), "city": current_user.city})

    if body.role not in ADMIN_ROLES:
        raise HTTPException(400, f"role must be one of {sorted(ADMIN_ROLES)}")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already registered")

    # Generate a unique placeholder CNIC (field is required in schema)
    for _ in range(20):
        cnic = f"ADMIN-{random.randint(10000,99999)}-{random.randint(100,999)}"
        if not db.query(User).filter(User.cnic == cnic).first():
            break

    user = User(
        first_name         = body.first_name.strip(),
        last_name          = body.last_name.strip(),
        email              = body.email.strip().lower(),
        cnic               = cnic,
        hashed_password    = hash_password(body.password),
        role               = body.role,
        city               = body.city.lower() if body.city else None,
        notification_email = body.notification_email.strip() if body.notification_email else None,
    )
    db.add(user)
    db.flush()

    if body.role == "dept_officer" and body.city and body.department:
        routing = RoutingTable(
            city            = body.city.lower(),
            department      = body.department.lower(),
            department_name = body.dept_name or body.department.upper(),
            officer_id      = user.id,
            is_active       = True,
        )
        db.add(routing)

    db.commit()
    db.refresh(user)
    logger.info(f"Admin user created: {user.email} ({user.role}) by {current_user.email}")
    return _user_dict(user, db)


# ── PATCH /admin/users/{id} ─────────────────────────────────────────────────

class UpdateUserBody(BaseModel):
    city:               Optional[str]  = None
    department:         Optional[str]  = None
    is_active:          Optional[bool] = None
    notification_email: Optional[str]  = None


@router.patch("/{user_id}")
def update_user(
    user_id:      int,
    body:         UpdateUserBody,
    current_user: User    = Depends(ALL_ADMIN),
    db:           Session = Depends(get_db),
):
    caller_role = (current_user.role or "").lower()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # Users may update only their own notification_email
    is_self = user.id == current_user.id
    if is_self and caller_role not in ("super_admin", "city_admin"):
        # dept_officer: only allow notification_email update on self
        allowed_fields = {"notification_email"}
        payload = body.dict(exclude_none=True)
        if not payload.keys() <= allowed_fields:
            raise HTTPException(403, "Officers may only update their notification email")
    elif not is_self and caller_role not in ("super_admin", "city_admin"):
        raise HTTPException(403, "Insufficient permissions to modify other users")
    elif not is_self and caller_role == "city_admin":
        # city_admin can only edit dept_officers in their own city
        if user.city != current_user.city or (user.role or "") != "dept_officer":
            raise HTTPException(403, "City admins may only modify officers in their own city")

    if body.city is not None:
        user.city = body.city.lower()

    if body.notification_email is not None:
        user.notification_email = body.notification_email.strip() or None

    # Deactivate routing rows if officer is being deactivated
    if body.is_active is False:
        db.query(RoutingTable).filter_by(officer_id=user_id).update({"is_active": False})

    # Reactivate or change dept for dept_officer
    if body.department is not None and (user.role or "").lower() == "dept_officer":
        db.query(RoutingTable).filter_by(officer_id=user_id).update({"is_active": False})
        if body.department and user.city:
            new_routing = RoutingTable(
                city            = user.city,
                department      = body.department.lower(),
                department_name = body.department.upper(),
                officer_id      = user_id,
                is_active       = True,
            )
            db.add(new_routing)

    db.commit()
    db.refresh(user)
    logger.info(f"User {user_id} updated by {current_user.email}")
    return _user_dict(user, db)
