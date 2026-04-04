# backend/routers/admin/dashboard.py
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
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
        "total": len(reports),
        "totals": {
            "reports":     len(reports),
            "pending":     status_counts.get("PENDING", 0),
            "verified":    status_counts.get("VERIFIED", 0),
            "in_progress": status_counts.get("IN_PROGRESS", 0),
            "resolved":    status_counts.get("RESOLVED", 0),
        },
        "kanban_counts": dict(stage_counts),
    }


@router.get("/analytics")
def dashboard_analytics(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    """Time-series analytics: trend, category breakdown, dept breakdown, stage distribution."""
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

    cutoff  = datetime.now(timezone.utc) - timedelta(days=days)
    trend_q = q.filter(Report.created_at >= cutoff)

    daily = (
        trend_q
        .with_entities(
            func.date(Report.created_at).label("day"),
            func.count(Report.id).label("total"),
        )
        .group_by(func.date(Report.created_at))
        .order_by(func.date(Report.created_at))
        .all()
    )

    all_reports = q.all()

    category_breakdown = Counter(
        r.category.value if r.category else "OTHER" for r in all_reports
    )
    stage_distribution = Counter(
        r.kanban_stage.value if r.kanban_stage else "NEW" for r in all_reports
    )
    dept_breakdown = Counter(
        r.assigned_department for r in all_reports if r.assigned_department
    )

    # Avg resolution "days" per dept (placeholder: count resolved per dept)
    resolved = [r for r in all_reports if r.kanban_stage and r.kanban_stage.value == "RESOLVED"]
    dept_resolved = Counter(r.assigned_department for r in resolved if r.assigned_department)

    return {
        "days":               days,
        "trend":              [{"date": str(row.day), "total": row.total} for row in daily],
        "category_breakdown": dict(category_breakdown),
        "stage_distribution": dict(stage_distribution),
        "dept_breakdown":     dict(dept_breakdown),
        "dept_resolved":      dict(dept_resolved),
        "total":              len(all_reports),
        "resolved":           len(resolved),
    }
