# backend/routers/admin/audit.py
"""
GET /admin/audit-logs  — system-wide audit trail.
Role scoping:
  super_admin  → all logs
  city_admin   → logs for reports in their city
  dept_officer → logs for reports in their dept (their city + dept)
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.database import SessionLocal
from model.report_logs import ReportLog
from model.report import Report
from model.routing_table import RoutingTable
from model.users import User
from utils.auth_utils import get_current_user
from utils.rbac import require_roles

router = APIRouter(prefix="/admin/audit-logs", tags=["Admin Audit"])

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
def list_audit_logs(
    report_id: Optional[int] = Query(None),
    skip:      int           = Query(0,  ge=0),
    limit:     int           = Query(50, ge=1, le=200),
    current_user: User    = Depends(ALL_ADMIN),
    db:           Session = Depends(get_db),
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

    if report_id:
        q = q.filter(ReportLog.report_id == report_id)

    total = q.count()
    logs  = q.order_by(ReportLog.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for log in logs:
        result.append({
            "id":                  log.id,
            "report_id":           log.report_id,
            "display_id":          f"#SR-{log.report_id:04d}",
            "changed_by":          log.changed_by,
            "previous_stage":      log.previous_stage,
            "new_stage":           log.new_stage,
            "note":                log.note,
            "ai_managed":          log.ai_managed,
            "assigned_city":       log.assigned_city,
            "assigned_department": log.assigned_department,
            "created_at":          log.created_at.isoformat() if log.created_at else None,
        })

    return {"logs": result, "total": total}
