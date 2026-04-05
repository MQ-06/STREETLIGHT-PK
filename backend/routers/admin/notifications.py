# backend/routers/admin/notifications.py
"""
GET /admin/notifications
Returns recent activity feed for the current user's scope.
Combines: new reports assigned (ai_managed), stage changes by humans, and notes.
Role-scoped same as audit logs.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.database import SessionLocal
from model.report_logs import ReportLog
from model.report import Report
from model.routing_table import RoutingTable
from model.users import User
from utils.rbac import require_roles

router = APIRouter(prefix="/admin/notifications", tags=["Admin Notifications"])

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
def get_notifications(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    role = (current_user.role or "").lower()

    q = db.query(ReportLog).join(Report, ReportLog.report_id == Report.id)

    if role == "dept_officer":
        routing = db.query(RoutingTable).filter_by(
            officer_id=current_user.id, is_active=True
        ).first()
        if routing:
            q = q.filter(
                Report.assigned_city       == routing.city,
                Report.assigned_department == routing.department,
            )
        else:
            q = q.filter(ReportLog.changed_by == str(current_user.id))
    elif role == "city_admin" and current_user.city:
        q = q.filter(Report.assigned_city == current_user.city)

    logs = q.order_by(ReportLog.created_at.desc()).limit(limit).all()

    items = []
    for log in logs:
        # Determine notification type and message
        if log.ai_managed and log.assigned_city:
            kind    = "assigned"
            message = f"New report auto-routed to {(log.assigned_department or '').upper()}"
        elif log.new_stage == "RESOLVED":
            kind    = "resolved"
            message = f"Report marked as Resolved"
        elif log.new_stage and log.previous_stage:
            kind    = "stage"
            message = f"{log.previous_stage} → {log.new_stage}"
        elif log.note and not log.new_stage:
            kind    = "note"
            message = f"Note: {log.note[:60]}{'…' if len(log.note or '') > 60 else ''}"
        else:
            kind    = "update"
            message = log.note or "Status updated"

        items.append({
            "id":         log.id,
            "kind":       kind,
            "report_id":  log.report_id,
            "display_id": f"#SR-{log.report_id:04d}",
            "message":    message,
            "ai_managed": log.ai_managed,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })

    return {"notifications": items, "total": len(items)}
