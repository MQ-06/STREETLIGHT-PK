# backend/agents/agent_tools.py

from model.report import Report
from model.report_logs import ReportLog
from agents.agent_config import (
    SCORE_AUTO_VERIFY,
    SCORE_REVIEW_NEEDED,
)
from datetime import datetime, timezone


def execute_action(db, report: Report, action: dict):

    act = action["action"]

    # ── AUTO VERIFY ─────────────────────
    if act == "AUTO_VERIFY":
        report.status = "VERIFIED"
        report.kanban_stage = "VERIFIED"

        log(db, report, "PENDING", "VERIFIED", "agent auto verified")

    # ── REJECT ──────────────────────────
    elif act == "REJECT":
        report.status = "REJECTED"

        log(db, report, "PENDING", "REJECTED", "low confidence score")

    # ── REVIEW ──────────────────────────
    elif act == "MOVE_REVIEW":
        report.status = "REVIEW_NEEDED"

        log(db, report, "PENDING", "REVIEW_NEEDED", "needs officer review")

    # ── ESCALATE ────────────────────────
    elif act == "ESCALATE":
        report.status = "IN_PROGRESS"

        log(db, report, "IN_PROGRESS", "IN_PROGRESS", "escalated by agent")


def log(db, report, prev, new, note):

    entry = ReportLog(
        report_id=report.id,
        changed_by="agent",
        previous_status=prev,
        new_status=new,
        note=note,
        ai_managed=True,
        assigned_city=report.assigned_city,
        assigned_department=report.assigned_department,
        assigned_officer_id=report.assigned_officer_id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(entry)