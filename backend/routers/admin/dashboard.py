# backend/routers/admin/dashboard.py
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import SessionLocal
from model.report import Report, KanbanStage
from model.users import User
from model.routing_table import RoutingTable
from utils.rbac import require_roles

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])

ALL_ADMIN = require_roles(
    "super_admin", "city_admin", "dept_officer",
    # legacy roles kept for backward compat
    "municipal_officer", "department_head", "city_planner", "system_admin",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/overview")
def dashboard_overview(
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    role = (current_user.role or "").lower()

    q = db.query(Report)

    if role == "dept_officer":
        routing = db.query(RoutingTable).filter_by(
            officer_id=current_user.id, is_active=True
        ).first()
        if routing:
            q = q.filter(
                Report.assigned_city       == routing.city,
                Report.assigned_department == routing.department,
            )
    elif role == "city_admin" and current_user.city:
        q = q.filter(Report.assigned_city == current_user.city)

    reports = q.all()

    status_counts = Counter(r.status.value if r.status else "UNKNOWN" for r in reports)
    stage_counts  = Counter(
        r.kanban_stage.value if r.kanban_stage else "NEW" for r in reports
    )

    return {
        "viewer_role": role,
        "viewer_city": current_user.city,
        "totals": {
            "reports":     len(reports),
            "pending":     status_counts.get("PENDING", 0),
            "verified":    status_counts.get("VERIFIED", 0),
            "in_progress": status_counts.get("IN_PROGRESS", 0),
            "resolved":    status_counts.get("RESOLVED", 0),
        },
        "kanban_counts": dict(stage_counts),
    }
