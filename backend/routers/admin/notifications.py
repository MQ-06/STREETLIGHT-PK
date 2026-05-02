# backend/routers/admin/notifications.py
"""
GET /admin/notifications

Important-only activity for the bell dropdown (not a full audit mirror).

Included (role-scoped, same joins/filters as audit logs):
  • Report routed / assignment metadata logged by routing or agents (ai_managed + city).
  • Milestone Kanban stages: awaiting citizen confirmation, resolved, closed.
  • Work bounced back from awaiting-feedback → in progress (e.g. citizen rejected fix).
  • Failure / escalation phrases in notes (after-image rejected, agent rejected, blockchain
    failure, resolved-without-photo rollback, etc.).

Excluded: routine stage churn (e.g. every NEW→VERIFIED drag), generic internal notes,
  and other low-signal rows — use Audit Log for the full trail.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, or_
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


def _important_logs_clause():
    """SQL predicate: keep high-signal rows only."""
    routed = and_(ReportLog.ai_managed.is_(True), ReportLog.assigned_city.isnot(None))
    milestones = ReportLog.new_stage.in_(
        ("RESOLVED", "CLOSED", "AWAITING_FEEDBACK"),
    )
    bounce_back = and_(
        ReportLog.previous_stage == "AWAITING_FEEDBACK",
        ReportLog.new_stage == "IN_PROGRESS",
    )
    note = ReportLog.note
    urgent_note = or_(
        note.ilike("%citizen rejected%"),
        note.ilike("%after-image failed%"),
        note.ilike("%after-image rejected%"),
        note.ilike("%needs officer review%"),
        note.ilike("%agent rejected%"),
        note.ilike("%agent flagged%"),
        note.ilike("%blockchain%failed%"),
        note.ilike("%resolved attempted but no after-image%"),
        note.ilike("%after-image required%"),
        note.ilike("%routing failed%"),
    )
    return or_(routed, milestones, bounce_back, urgent_note)


def _format_item(log: ReportLog) -> tuple[str, str]:
    """Return (kind, message) for UI — kinds match Topbar KIND_STYLE keys."""
    if log.ai_managed and log.assigned_city:
        dept = (log.assigned_department or "").upper()
        city = log.assigned_city or ""
        return "assigned", f"Report routed{f' to {dept}' if dept else ''}{f' ({city})' if city else ''}"

    if log.new_stage == "CLOSED":
        return "resolved", "Complaint closed"

    if log.new_stage == "RESOLVED":
        return "resolved", "Marked resolved — citizen / blockchain steps may follow"

    if log.new_stage == "AWAITING_FEEDBACK":
        return "stage", "Awaiting citizen confirmation (fix submitted)"

    if log.previous_stage == "AWAITING_FEEDBACK" and log.new_stage == "IN_PROGRESS":
        return "stage", "Back to in progress (citizen rejected or verification failed)"

    raw_note = log.note or ""
    low = raw_note.lower()
    if any(
        k in low
        for k in (
            "blockchain",
            "after-image failed",
            "after-image rejected",
            "citizen rejected",
            "agent rejected",
            "needs officer review",
            "routing failed",
            "after-image required",
            "resolved attempted but no after-image",
        )
    ):
        short = raw_note.strip().replace("\n", " ")
        if len(short) > 90:
            short = short[:87] + "…"
        return "update", short

    return "update", raw_note.strip()[:90] or "Update on this report"


@router.get("")
def get_notifications(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    role = (current_user.role or "").lower()

    q = db.query(ReportLog).join(Report, ReportLog.report_id == Report.id)
    q = q.filter(_important_logs_clause())

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
        kind, message = _format_item(log)
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
