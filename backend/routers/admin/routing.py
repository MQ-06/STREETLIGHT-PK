# backend/routers/admin/routing.py
"""
GET /admin/routing  — returns the active routing table rows.
Role scoping:
  super_admin  → all rows (optionally filtered by ?city=)
  city_admin   → rows for their city
  dept_officer → their own row
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from db.database import SessionLocal
from model.routing_table import RoutingTable
from model.users import User
from utils.auth_utils import get_current_user
from utils.rbac import require_roles

router = APIRouter(prefix="/admin/routing", tags=["Admin Routing"])

ALL_ADMIN = require_roles(
    "super_admin", "city_admin", "dept_officer",
    "municipal_officer", "department_head", "city_planner", "system_admin",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def list_routing(
    city: Optional[str] = Query(None),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    role = (current_user.role or "").lower()
    q = db.query(RoutingTable).options(joinedload(RoutingTable.officer))

    if role == "city_admin" and current_user.city:
        q = q.filter(RoutingTable.city == current_user.city)
    elif role == "dept_officer":
        q = q.filter(RoutingTable.officer_id == current_user.id)
    else:
        # super_admin: optional city filter
        if city:
            q = q.filter(RoutingTable.city == city.lower())

    rows = q.order_by(RoutingTable.city, RoutingTable.department).all()

    result = []
    for r in rows:
        officer = r.officer
        result.append({
            "id":              r.id,
            "city":            r.city,
            "department":      r.department,
            "department_name": r.department_name,
            "officer_id":      r.officer_id,
            "officer_name":    f"{officer.first_name} {officer.last_name}" if officer else None,
            "officer_email":   (officer.notification_email or officer.email) if officer else None,
            "is_active":       r.is_active,
        })

    return {"routing": result, "total": len(result)}
