# backend/services/routing/routing_service.py
"""
Orchestrates the full auto-routing pipeline for a newly created report:

  Step 1 — Detect city   (GPS → city slug)
  Step 2 — Map dept      (city + issue_type → department slug)
  Step 3 — Look up officer (query routing_table)
  Step 4 — Update report  (assigned_city, assigned_department,
                            assigned_officer_id, assigned_at, kanban_stage=NEW)
  Step 5 — Write audit log (report_logs, ai_managed=True)

Always non-blocking — all exceptions are caught and logged.
A routing failure must never crash the report creation endpoint.

Returns a dict summarising the routing outcome for logging.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from model.report import Report, KanbanStage
from model.routing_table import RoutingTable
from model.report_logs import ReportLog
from services.routing.city_detector import detect_city, get_city_display_name
from services.routing.dept_mapper import map_issue_to_department, get_department_display_name
from utils.email_service import send_new_report_notification

logger = logging.getLogger(__name__)


def route_report(
    db: Session,
    report: Report,
    lat: float,
    lng: float,
    issue_type: str,          # lowercased AI predicted class: "pothole" | "garbage"
) -> dict:
    """
    Auto-routes a report to the responsible Department Officer.

    Args:
        db:         SQLAlchemy session (already open, caller commits)
        report:     Persisted Report ORM instance (id already set)
        lat:        Submission latitude
        lng:        Submission longitude
        issue_type: Lowercased AI class ("pothole" or "garbage")

    Returns:
        dict with keys: success, city, department, officer_id, officer_name, note
    """
    result = {
        "success":      False,
        "city":         None,
        "department":   None,
        "officer_id":   None,
        "officer_name": None,
        "note":         "",
    }

    try:
        # ── Step 1: Detect city ─────────────────────────────────────────
        city = detect_city(lat, lng)
        if not city:
            note = (
                f"GPS ({lat:.4f}, {lng:.4f}) is outside all configured city boundaries. "
                "Report saved but not routed — requires manual assignment."
            )
            logger.warning(f"🚦 routing: report ID={report.id} — {note}")
            _write_log(
                db, report,
                note=note,
                previous_stage=None,
                new_stage=KanbanStage.NEW.value,
            )
            report.kanban_stage = KanbanStage.NEW
            db.flush()
            result["note"] = note
            return result

        result["city"] = city

        # ── Step 2: Map issue type → department ────────────────────────
        dept = map_issue_to_department(city, issue_type)
        if not dept:
            note = (
                f"No department mapping for ({city}, {issue_type}). "
                "Report saved but not routed — requires manual assignment."
            )
            logger.warning(f"🚦 routing: report ID={report.id} — {note}")
            _write_log(
                db, report,
                note=note,
                assigned_city=city,
                previous_stage=None,
                new_stage=KanbanStage.NEW.value,
            )
            report.assigned_city = city
            report.kanban_stage  = KanbanStage.NEW
            db.flush()
            result["note"] = note
            return result

        result["department"] = dept

        # ── Step 3: Look up officer in routing_table ───────────────────
        routing_row: Optional[RoutingTable] = (
            db.query(RoutingTable)
            .filter(
                RoutingTable.city       == city,
                RoutingTable.department == dept,
                RoutingTable.is_active  == True,
            )
            .first()
        )

        if not routing_row:
            note = (
                f"No active routing row for city='{city}', dept='{dept}'. "
                "Report saved but not routed — requires manual assignment."
            )
            logger.warning(f"🚦 routing: report ID={report.id} — {note}")
            _write_log(
                db, report,
                note=note,
                assigned_city=city,
                assigned_department=dept,
                previous_stage=None,
                new_stage=KanbanStage.NEW.value,
            )
            report.assigned_city       = city
            report.assigned_department = dept
            report.kanban_stage        = KanbanStage.NEW
            db.flush()
            result["note"] = note
            return result

        officer    = routing_row.officer
        officer_id = officer.id
        officer_name = f"{officer.first_name} {officer.last_name}"
        dept_display = get_department_display_name(dept)
        city_display = get_city_display_name(city)

        result["officer_id"]   = officer_id
        result["officer_name"] = officer_name

        # ── Step 4: Update the report ──────────────────────────────────
        now = datetime.now(timezone.utc)
        report.assigned_city       = city
        report.assigned_department = dept
        report.assigned_officer_id = officer_id
        report.assigned_at         = now
        report.kanban_stage        = KanbanStage.NEW

        # ── Step 5: Write audit log ────────────────────────────────────
        note = (
            f"Auto-routed to {officer_name} ({dept_display}, {city_display}). "
            f"Kanban stage set to NEW."
        )
        _write_log(
            db, report,
            note=note,
            assigned_city=city,
            assigned_department=dept,
            assigned_officer_id=officer_id,
            previous_stage=None,
            new_stage=KanbanStage.NEW.value,
            previous_status=None,
            new_status=report.status.value if report.status else None,
        )

        db.flush()  # persist within caller's transaction (caller commits)

        result["success"] = True
        result["note"]    = note

        logger.info(
            f"✅ routing: report ID={report.id} → "
            f"city={city}, dept={dept}, officer='{officer_name}' (id={officer_id})"
        )

        # ── Step 6: Email notification (non-blocking) ─────────────��────
        notif_email = getattr(officer, "notification_email", None)
        if notif_email:
            try:
                send_new_report_notification(
                    to_email     = notif_email,
                    officer_name = officer_name,
                    report_id    = report.id,
                    display_id   = getattr(report, "display_id", None) or f"SL-{report.id:05d}",
                    category     = report.category.value if report.category else "OTHER",
                    severity     = getattr(report, "severity", None) or "unknown",
                    city         = city,
                    department   = dept,
                    description  = getattr(report, "description", None),
                    lat          = lat,
                    lng          = lng,
                )
            except Exception as email_exc:
                logger.warning(f"⚠️ Email notification failed (non-blocking): {email_exc}")

    except Exception as exc:
        result["note"] = f"Routing failed (non-blocking): {exc}"
        logger.error(
            f"❌ routing: unexpected error for report ID={report.id} — {exc}",
            exc_info=True,
        )

    return result


# ── Private helper ──────────────────────────────────────────────────────────

def _write_log(
    db: Session,
    report: Report,
    note: str,
    assigned_city: Optional[str]        = None,
    assigned_department: Optional[str]  = None,
    assigned_officer_id: Optional[int]  = None,
    previous_stage: Optional[str]       = None,
    new_stage: Optional[str]            = None,
    previous_status: Optional[str]      = None,
    new_status: Optional[str]           = None,
) -> None:
    """Appends one row to report_logs. Does NOT commit."""
    log_entry = ReportLog(
        report_id           = report.id,
        changed_by          = "agent",
        previous_stage      = previous_stage,
        new_stage           = new_stage,
        previous_status     = previous_status,
        new_status          = new_status,
        assigned_city       = assigned_city,
        assigned_department = assigned_department,
        assigned_officer_id = assigned_officer_id,
        note                = note,
        ai_managed          = True,
    )
    db.add(log_entry)
