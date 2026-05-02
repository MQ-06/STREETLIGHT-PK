"""
Notify the citizen (report owner) when their report's workflow changes.
Uses in-app Notification rows + best-effort FCM (same as resolution flow).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from db.database import SessionLocal
from utils.notifications import NotificationService
from utils.push import send_push_to_user

logger = logging.getLogger(__name__)


def _notify(
    reporter_user_id: Optional[int],
    report_id: int,
    title: str,
    body: str,
    notification_type: str,
    data: Dict[str, Any],
) -> None:
    if not reporter_user_id:
        return

    ndb = SessionLocal()
    try:
        NotificationService(ndb).create(
            user_id=reporter_user_id,
            type=notification_type,
            title=title,
            body=body,
            entity_type="report",
            entity_id=report_id,
            data=data,
            dedupe_key=None,
        )
    except Exception as exc:
        logger.warning("Reporter in-app notify failed report=%s: %s", report_id, exc)
    finally:
        ndb.close()

    pdb = SessionLocal()
    try:
        push_data = {str(k): str(v) for k, v in data.items()}
        push_data["type"] = notification_type
        push_data["report_id"] = str(report_id)
        send_push_to_user(
            pdb,
            user_id=reporter_user_id,
            title=title,
            body=body,
            data=push_data,
        )
    except Exception as exc:
        logger.warning("Reporter push failed report=%s: %s", report_id, exc)
    finally:
        pdb.close()


def _stage_label(stage: Optional[str]) -> str:
    if not stage:
        return "Updated"
    return stage.replace("_", " ").title()


def notify_reporter_kanban_stage_change(
    *,
    report_id: int,
    reporter_user_id: Optional[int],
    previous_stage: Optional[str],
    new_stage: str,
    status_value: Optional[str] = None,
) -> None:
    """
    Called when staff moves the Kanban column (admin PATCH).
    Skips RESOLVED / AWAITING_FEEDBACK — resolution_agent already notifies the citizen.
    """
    if not reporter_user_id:
        return
    if new_stage in ("RESOLVED", "AWAITING_FEEDBACK"):
        return
    if previous_stage == new_stage:
        return

    display = f"#SR-{report_id:04d}"
    title = "Report status updated"
    body = (
        f"{display} is now {_stage_label(new_stage)}"
        + (f" ({status_value})" if status_value else "")
        + ". Open the app for details."
    )
    _notify(
        reporter_user_id,
        report_id,
        title,
        body,
        "REPORT_STAGE",
        {"route": "/home", "kanban_stage": new_stage},
    )


def notify_reporter_routed_to_municipal(
    *,
    report_id: int,
    reporter_user_id: Optional[int],
    city: str,
    department: str,
) -> None:
    if not reporter_user_id:
        return
    display = f"#SR-{report_id:04d}"
    title = "Report assigned"
    body = (
        f"{display} was sent to the municipal team "
        f"({department.upper()} · {city})."
    )
    _notify(
        reporter_user_id,
        report_id,
        title,
        body,
        "REPORT_ROUTED",
        {"route": "/home", "city": city, "department": department},
    )


def notify_reporter_agent_action(*, report_id: int, reporter_user_id: Optional[int], action: str) -> None:
    """Complaint-agent batch: short copy per automated transition."""
    if not reporter_user_id:
        return

    display = f"#SR-{report_id:04d}"
    if action == "AUTO_VERIFY":
        title, body = (
            "Report verified",
            f"{display} passed automatic checks and is with the municipal team.",
        )
        typ = "AGENT_VERIFY"
    elif action == "VERIFY_AND_ASSIGN":
        title, body = (
            "Community verified",
            f"{display} reached enough community support and was verified.",
        )
        typ = "AGENT_COMMUNITY_VERIFY"
    elif action == "REJECT":
        title, body = (
            "More review needed",
            f"{display} could not be auto-verified. Staff will review your photo.",
        )
        typ = "AGENT_REVIEW"
    elif action == "MOVE_REVIEW":
        title, body = (
            "Manual review",
            f"{display} needs a quick staff review before next steps.",
        )
        typ = "AGENT_REVIEW"
    elif action == "NEEDS_LLM":
        title, body = (
            "Report updated",
            f"{display} was flagged for follow-up by the system.",
        )
        typ = "AGENT_ESCALATION"
    else:
        return

    _notify(
        reporter_user_id,
        report_id,
        title,
        body,
        typ,
        {"route": "/home"},
    )
