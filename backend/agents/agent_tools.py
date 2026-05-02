# backend/agents/agent_tools.py

from model.report import Report, ReportStatus, KanbanStage  # ✅ import enums
from model.report_logs import ReportLog
from agents.agent_llm import ask_llm
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def execute_action(db, report: Report, action: dict):
    act = action["action"]

    # ── AUTO VERIFY ─────────────────────
    if act == "AUTO_VERIFY":
        prev = report.status
        report.status = ReportStatus.VERIFIED          # ✅ enum
        report.kanban_stage = KanbanStage.VERIFIED     # ✅ enum
        log(db, report, prev, ReportStatus.VERIFIED, "Agent auto-verified: high confidence score")

    # ── REJECT ──────────────────────────
    elif act == "REJECT":
        prev = report.status
        # ✅ No REJECTED enum value — use REVIEW_NEEDED and flag it, 
        # OR add REJECTED to your enum. For now we use REVIEW_NEEDED + note.
        report.status = ReportStatus.REVIEW_NEEDED
        report.verification_status = "REJECTED"        # this column is a plain String ✅
        report.kanban_stage = KanbanStage.PENDING_VERIFICATION
        log(db, report, prev, ReportStatus.REVIEW_NEEDED, "Agent rejected: low confidence score")

    # ── MOVE TO REVIEW ───────────────────
    elif act == "MOVE_REVIEW":
        prev = report.status
        report.status = ReportStatus.REVIEW_NEEDED     # ✅ enum
        report.kanban_stage = KanbanStage.PENDING_VERIFICATION
        log(db, report, prev, ReportStatus.REVIEW_NEEDED, "Agent flagged: needs officer review")

    # ── VERIFY AND ASSIGN (community trigger) ───
    elif act == "VERIFY_AND_ASSIGN":
        prev = report.status
        report.status = ReportStatus.VERIFIED          # ✅
        report.kanban_stage = KanbanStage.VERIFIED
        log(db, report, prev, ReportStatus.VERIFIED, "Agent verified: community votes threshold reached")

    # ── LLM FALLBACK (handles escalation) ───────
    elif act == "NEEDS_LLM":
        note = ask_llm(report)
        prev = report.status
        report.status = ReportStatus.IN_PROGRESS       # stays IN_PROGRESS but gets a note
        log(db, report, prev, ReportStatus.IN_PROGRESS, f"Agent escalated (LLM): {note}")

    # ── NO ACTION ───────────────────────
    elif act == "NO_OP":
        logger.info(f"📋 Report {report.id} — no action needed")


# ───────────────────────────────────────
# CENTRAL LOGGING FUNCTION
# ───────────────────────────────────────
def log(db, report, prev, new, note):
    entry = ReportLog(
        report_id=report.id,
        changed_by="agent",
        previous_status=str(prev.value) if hasattr(prev, 'value') else str(prev),
        new_status=str(new.value) if hasattr(new, 'value') else str(new),
        note=note,
        ai_managed=True,
        assigned_city=report.assigned_city,
        assigned_department=report.assigned_department,
        assigned_officer_id=report.assigned_officer_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(entry)
    logger.info(f"📝 Log: report {report.id} | {prev} → {new} | {note}")