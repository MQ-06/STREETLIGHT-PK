# backend/agents/agent_rules.py

from model.report import Report


def decide_action(report: Report):

    score = report.combined_score or 0
    status = report.status
    community = report.community_score or 0

    # ── NEW REPORT RULES ─────────────────────
    if status == "PENDING":

        if score >= 85:
            return {"action": "AUTO_VERIFY"}

        if score < 60:
            return {"action": "REJECT"}

        if 60 <= score < 85:
            return {"action": "MOVE_REVIEW"}

    # ── COMMUNITY TRIGGER ────────────────────
    if status == "PENDING" and community >= 3:
        return {"action": "VERIFY_AND_ASSIGN"}

    # ── STUCK REPORTS ────────────────────────
    if status == "IN_PROGRESS" and report_stalled(report):
        return {"action": "ESCALATE"}

    # default
    return {"action": "NO_OP"}


def report_stalled(report):
    from datetime import datetime, timezone

    if not report.updated_at:
        return False

    hours = (datetime.now(timezone.utc) - report.updated_at).total_seconds() / 3600
    return hours > 48