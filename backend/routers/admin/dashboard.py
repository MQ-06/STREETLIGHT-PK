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

    # Build base filter conditions (reused across multiple aggregation queries)
    filters = []
    if role == "dept_officer":
        routing = db.query(RoutingTable).filter_by(
            officer_id=current_user.id, is_active=True
        ).first()
        if routing:
            filters = [
                Report.assigned_city       == routing.city,
                Report.assigned_department == routing.department,
            ]
    elif role == "city_admin" and current_user.city:
        filters = [Report.assigned_city == current_user.city]

    # Kanban stage counts — single GROUP BY query, no Python-side iteration
    stage_rows = (
        db.query(Report.kanban_stage, func.count(Report.id))
        .filter(*filters)
        .group_by(Report.kanban_stage)
        .all()
    )
    stage_counts = {
        (row[0].value if row[0] else "NEW"): row[1]
        for row in stage_rows
    }
    total = sum(stage_counts.values())

    # Status counts — single GROUP BY query
    status_rows = (
        db.query(Report.status, func.count(Report.id))
        .filter(*filters)
        .group_by(Report.status)
        .all()
    )
    status_counts = {
        (row[0].value if row[0] else "UNKNOWN"): row[1]
        for row in status_rows
    }

    # City breakdown — single GROUP BY query (super_admin only)
    city_breakdown = {}
    if role == "super_admin":
        terminal = (KanbanStage.RESOLVED, KanbanStage.CLOSED)
        city_rows = (
            db.query(
                Report.assigned_city,
                func.count(Report.id).label("total"),
                func.count(Report.id).filter(
                    Report.kanban_stage.in_(terminal)
                ).label("resolved"),
            )
            .group_by(Report.assigned_city)
            .all()
        )
        for city, city_total, city_resolved in city_rows:
            city_breakdown[city or "unknown"] = {
                "total":    city_total,
                "resolved": city_resolved,
            }

    return {
        "viewer_role":   role,
        "viewer_city":   current_user.city,
        "total":         total,
        "totals": {
            "reports":     total,
            "pending":     status_counts.get("PENDING", 0),
            "verified":    status_counts.get("VERIFIED", 0),
            "in_progress": status_counts.get("IN_PROGRESS", 0),
            "resolved":    status_counts.get("RESOLVED", 0),
        },
        "kanban_counts": stage_counts,
        "city_breakdown": city_breakdown,
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

    terminal_stages = {KanbanStage.RESOLVED, KanbanStage.CLOSED}
    resolved = [
        r for r in all_reports
        if r.kanban_stage and r.kanban_stage in terminal_stages
    ]
    dept_resolved = Counter(r.assigned_department for r in resolved if r.assigned_department)

    avg_resolution_hours = None
    hours_list = []
    for r in resolved:
        if r.created_at and r.updated_at:
            delta = r.updated_at - r.created_at
            hours_list.append(delta.total_seconds() / 3600.0)
    if hours_list:
        avg_resolution_hours = round(sum(hours_list) / len(hours_list), 1)

    answered = [
        r for r in all_reports
        if r.citizen_response in ("CONFIRMED", "REJECTED")
    ]
    citizen_confirmation_rate_pct = None
    if answered:
        confirmed_n = sum(1 for r in answered if r.citizen_response == "CONFIRMED")
        citizen_confirmation_rate_pct = round(100.0 * confirmed_n / len(answered), 1)

    return {
        "days":               days,
        "trend":              [{"date": str(row.day), "total": row.total} for row in daily],
        "category_breakdown": dict(category_breakdown),
        "stage_distribution": dict(stage_distribution),
        "dept_breakdown":     dict(dept_breakdown),
        "dept_resolved":      dict(dept_resolved),
        "total":              len(all_reports),
        "resolved":           len(resolved),
        "avg_resolution_hours": avg_resolution_hours,
        "citizen_confirmation_rate_pct": citizen_confirmation_rate_pct,
        "citizen_feedback_n": len(answered),
    }
