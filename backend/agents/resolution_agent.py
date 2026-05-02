# backend/agents/resolution_agent.py
"""
Resolution pipeline — runs after officer uploads after-image.

Flow:
  1. AI 3-check verification on after-image
  2. If passes → send FCM to citizen for confirmation
  3. Citizen confirms → finalize_resolution()
  4. OR auto_close_days pass → finalize_resolution()
  5. finalize_resolution() → RESOLVED → blockchain → CLOSED
"""
#agents/resolution_agent.py
import logging
from datetime import datetime, timezone
from db.database import SessionLocal
from model.report import Report, ReportStatus, KanbanStage
from model.report_logs import ReportLog
from agents.agent_config import AFTER_PHOTO_GPS_TOLERANCE_M, AUTO_CLOSE_DAYS
from sqlalchemy import or_

from blockchain.blockchain_service import blockchain_service
from utils.push import send_push_to_user

logger = logging.getLogger(__name__)


def process_resolution(report_id: int):
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return

        # After-image hai ya nahi?
        if not report.after_image_url:
            # After-image missing — officer ko notify karo, RESOLVED se wapas IN_PROGRESS
            logger.warning(f"⚠️ Report #{report_id} moved to RESOLVED but no after-image!")
            
            report.kanban_stage = KanbanStage.IN_PROGRESS
            report.status = ReportStatus.IN_PROGRESS

            log = ReportLog(
                report_id=report_id,
                changed_by="agent",
                previous_stage=KanbanStage.RESOLVED.value,
                new_stage=KanbanStage.IN_PROGRESS.value,
                note="RESOLVED attempted but no after-image uploaded. Returned to IN_PROGRESS.",
                ai_managed=True,
            )
            db.add(log)
            db.commit()

            # Officer ko push
            if report.assigned_officer_id:
                try:
                    send_push_to_user(
                        db,
                        user_id=report.assigned_officer_id,
                        title="After-image required ⚠️",
                        body=f"Report #SR-{report_id:04d}: Please upload after-image before resolving.",
                        data={"type": "AFTER_IMAGE_REQUIRED", "report_id": str(report_id)},
                    )
                except Exception:
                    pass
            return

        # After-image hai — FCM citizen ko bhejo
        _send_citizen_confirmation_request(report, db, "After-image verified by agent")
        db.commit()

    except Exception as e:
        logger.error(f"❌ process_resolution failed: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def _run_resolution_classifier(after_image_url: str, category) -> bool:
    """
    MVP: Returns True if after-image passes basic validation.
    Replace with actual ResNet18 'resolved' classifier call.
    
    Production implementation:
        result = ai_engine.classify_resolved(after_image_url, category)
        return result["resolved_confidence"] > 0.70
    """
    # For now: if Cloudinary URL is valid, pass
    if after_image_url and after_image_url.startswith("https://res.cloudinary.com"):
        return True
    return False


# ══════════════════════════════════════════════════════
# STEP 2 — SEND FCM TO CITIZEN FOR CONFIRMATION
# ══════════════════════════════════════════════════════

def _send_citizen_confirmation_request(report: Report, db, verification_note: str):
    """
    Sends FCM push notification to citizen:
    'Your issue has been fixed! Please confirm.'
    """
    citizen = report.reporter
    if not citizen:
        logger.warning(f"⚠️ No citizen found for report #{report.id} — auto-resolving")
        finalize_resolution(report.id, resolution_note="Auto-resolved: no citizen account")
        return

    display_id = f"#SR-{report.id:04d}"
    category   = report.category.value if report.category else "issue"

    try:
        send_push_to_user(
            db,
            user_id = citizen.id,
            title   = "Your issue has been fixed! ✅",
            body    = (
                f"The municipal team has resolved your {category} report "
                f"{display_id}. Please open the app to confirm."
            ),
            data    = {
                "type":            "RESOLUTION_CONFIRM",
                "route":           "/resolution_confirm",
                "report_id":       str(report.id),
                "after_image_url": report.after_image_url or "",
                "action":          "CONFIRM_OR_REJECT",
            },
        )

        report.resolution_notified_at = datetime.now(timezone.utc)
        # Stage stays AWAITING_FEEDBACK — citizen now has the ball

        log = ReportLog(
            report_id      = report.id,
            changed_by     = "agent",
            previous_stage = KanbanStage.AWAITING_FEEDBACK.value,
            new_stage      = KanbanStage.AWAITING_FEEDBACK.value,
            note           = f"AI verification passed ({verification_note}). FCM sent to citizen {citizen.id}.",
            ai_managed     = True,
        )
        db.add(log)
        logger.info(f"📱 FCM sent to citizen {citizen.id} for report #{report.id}")

    except Exception as e:
        logger.error(f"❌ FCM send failed for report #{report.id}: {e}")
        # FCM failed but don't crash — auto-resolve will kick in after N days


def _handle_verification_failure(report: Report, db, verification_note: str):
    """After-image failed AI check — move back to IN_PROGRESS, notify officer."""
    report.kanban_stage     = KanbanStage.IN_PROGRESS
    report.after_image_url  = None
    report.after_image_uploaded_at = None

    log = ReportLog(
        report_id      = report.id,
        changed_by     = "agent",
        previous_stage = KanbanStage.AWAITING_FEEDBACK.value,
        new_stage      = KanbanStage.IN_PROGRESS.value,
        note           = f"After-image FAILED verification: {verification_note}. Returned to IN_PROGRESS.",
        ai_managed     = True,
    )
    db.add(log)

    # Notify officer that after-image was rejected
    if report.assigned_officer_id:
        try:
            send_push_to_user(
                db,
                user_id = report.assigned_officer_id,
                title   = "After-image rejected ❌",
                body    = f"Report #SR-{report.id:04d}: After-image did not pass verification. Please re-upload.",
                data    = {"type": "AFTER_IMAGE_REJECTED", "report_id": str(report.id)},
            )
        except Exception as e:
            logger.warning(f"⚠️ Officer push failed: {e}")

    logger.warning(f"❌ After-image verification FAILED for report #{report.id}: {verification_note}")


# ══════════════════════════════════════════════════════
# STEP 3 — CITIZEN CONFIRMS (called from Flutter router)
# ══════════════════════════════════════════════════════

def citizen_confirm_resolution(report_id: int, user_id: int, confirmed: bool) -> dict:
    """
    Called when citizen taps Confirm or Reject in Flutter app.
    confirmed=True  → finalize_resolution()
    confirmed=False → move back to IN_PROGRESS, notify officer
    """
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"success": False, "error": "Report not found"}

        if report.reporter and report.reporter.id != user_id:
            return {"success": False, "error": "Not your report"}

        if report.kanban_stage != KanbanStage.AWAITING_FEEDBACK:
            return {"success": False, "error": f"Report not awaiting feedback. Current: {report.kanban_stage}"}

        if confirmed:
            report.citizen_response = "CONFIRMED"
            report.citizen_confirmed_at = datetime.now(timezone.utc)
            db.commit()

            result = finalize_resolution(
                report_id       = report_id,
                resolution_note = "Resolved — confirmed by citizen via app",
            )
            return result
        else:
            report.citizen_response = "REJECTED"
            report.citizen_confirmed_at = datetime.now(timezone.utc)
            report.kanban_stage = KanbanStage.IN_PROGRESS
            report.after_image_url = None
            report.after_image_uploaded_at = None

            log = ReportLog(
                report_id      = report_id,
                changed_by     = str(user_id),
                previous_stage = KanbanStage.AWAITING_FEEDBACK.value,
                new_stage      = KanbanStage.IN_PROGRESS.value,
                note           = "Citizen REJECTED resolution — issue still not fixed.",
                ai_managed     = False,
            )
            db.add(log)
            db.commit()

            # Notify officer
            if report.assigned_officer_id:
                try:
                    send_push_to_user(
                        db,
                        user_id = report.assigned_officer_id,
                        title   = "Citizen rejected resolution ❌",
                        body    = f"Report #SR-{report_id:04d}: Citizen says issue is not fixed.",
                        data    = {"type": "CITIZEN_REJECTED", "report_id": str(report_id)},
                    )
                except Exception:
                    pass

            return {"success": True, "action": "rejected", "stage": KanbanStage.IN_PROGRESS.value}

    except Exception as e:
        logger.error(f"❌ citizen_confirm_resolution error: {e}", exc_info=True)
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


# ══════════════════════════════════════════════════════
# STEP 4 — FINALIZE RESOLUTION (blockchain + CLOSED)
# ══════════════════════════════════════════════════════

def finalize_resolution(report_id: int, resolution_note: str = "Issue resolved") -> dict:
    """
    The final step — called after citizen confirms OR auto-close.
    
    1. status → RESOLVED + kanban_stage → RESOLVED
    2. blockchain_service.mark_resolved()  ← Blockchain Entry 2
    3. status → CLOSED + kanban_stage → CLOSED
    4. Send final FCM to citizen
    """
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"success": False, "error": "Report not found"}

        logger.info(f"🏁 Finalizing resolution for report #{report_id}")

        # ── 1. Mark RESOLVED ───────────────────────────────────────────────
        prev_stage      = report.kanban_stage.value if report.kanban_stage else "AWAITING_FEEDBACK"
        report.status   = ReportStatus.RESOLVED
        report.kanban_stage = KanbanStage.RESOLVED

        log_resolved = ReportLog(
            report_id      = report_id,
            changed_by     = "agent",
            previous_stage = prev_stage,
            new_stage      = KanbanStage.RESOLVED.value,
            previous_status= ReportStatus.IN_PROGRESS.value,
            new_status     = ReportStatus.RESOLVED.value,
            note           = f"RESOLVED: {resolution_note}",
            ai_managed     = True,
        )
        db.add(log_resolved)
        db.commit()

        # ── 2. Blockchain Entry 2 ──────────────────────────────────────────
        bc_result = blockchain_service.mark_resolved(
            complaint_id    = report_id,
            resolution_note = resolution_note,
        )

        if bc_result.get("success"):
            tx_hash = bc_result.get("tx_hash", "")
            logger.info(f"⛓️  Blockchain Entry 2 written. TX: {tx_hash}")

            # ── 3. Mark CLOSED after blockchain confirms ───────────────────
            report.status              = ReportStatus.CLOSED
            report.kanban_stage        = KanbanStage.CLOSED
            report.blockchain_resolve_tx = tx_hash
            report.closed_at           = datetime.now(timezone.utc)

            log_closed = ReportLog(
                report_id       = report_id,
                changed_by      = "agent",
                previous_stage  = KanbanStage.RESOLVED.value,
                new_stage       = KanbanStage.CLOSED.value,
                previous_status = ReportStatus.RESOLVED.value,
                new_status      = ReportStatus.CLOSED.value,
                note            = f"CLOSED: Blockchain Entry 2 confirmed. TX: {tx_hash}",
                ai_managed      = True,
            )
            db.add(log_closed)

        else:
            # Blockchain failed — keep RESOLVED, retry in next agent cycle
            bc_error = bc_result.get("error", "unknown")
            logger.error(f"❌ Blockchain failed for report #{report_id}: {bc_error}")
            log_bc_fail = ReportLog(
                report_id      = report_id,
                changed_by     = "agent",
                note           = f"⚠️ Blockchain Entry 2 FAILED: {bc_error}. Will retry.",
                ai_managed     = True,
            )
            db.add(log_bc_fail)

        db.commit()

        # ── 4. Final FCM to citizen ────────────────────────────────────────
        if report.reporter:
            try:
                send_push_to_user(
                    db,
                    user_id = report.reporter.id,
                    title   = "Complaint Closed ✅",
                    body    = (
                        f"Your report #SR-{report_id:04d} is officially closed. "
                        f"Thank you for making your city better!"
                    ),
                    data    = {
                        "type":      "COMPLAINT_CLOSED",
                        "report_id": str(report_id),
                        "tx_hash":   bc_result.get("tx_hash", ""),
                    },
                )
            except Exception as e:
                logger.warning(f"⚠️ Final FCM failed (non-blocking): {e}")

        logger.info(f"✅ Report #{report_id} fully CLOSED")
        return {
            "success":     True,
            "report_id":   report_id,
            "stage":       report.kanban_stage.value,
            "blockchain":  bc_result,
        }

    except Exception as e:
        logger.error(f"❌ finalize_resolution error: {e}", exc_info=True)
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


# ══════════════════════════════════════════════════════
# STEP 5 — AUTO-CLOSE (called by agent scheduler)
# ══════════════════════════════════════════════════════

def check_auto_close(db):
    """
    Called every agent cycle (every 15 min).
    If report is AWAITING_FEEDBACK and N days have passed
    since resolution_notified_at → auto-resolve.
    """
    from datetime import timedelta
    from sqlalchemy import and_

    cutoff = datetime.now(timezone.utc) - timedelta(days=AUTO_CLOSE_DAYS)

    stale_reports = db.query(Report).filter(
        and_(
            Report.kanban_stage == KanbanStage.AWAITING_FEEDBACK,
            Report.resolution_notified_at != None,
            Report.resolution_notified_at <= cutoff,
            or_(
                Report.citizen_response.is_(None),
                Report.citizen_response == "PENDING",
            ),
        )
    ).all()

    for report in stale_reports:
        logger.info(
            f"⏰ Auto-closing report #{report.id} "
            f"— {AUTO_CLOSE_DAYS} days passed with no citizen response"
        )
        finalize_resolution(
            report_id       = report.id,
            resolution_note = f"Auto-resolved after {AUTO_CLOSE_DAYS} days — no citizen response",
        )