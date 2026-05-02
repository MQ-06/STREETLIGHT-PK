# backend/agents/complaint_agent.py

from db.database import SessionLocal
from model.report import Report, ReportStatus  # ✅ import enum
from agents.agent_rules import decide_action
from agents.agent_tools import execute_action
from agents.agent_lock import acquire_lock, release_lock
from agents.resolution_agent import check_auto_close
import logging

logger = logging.getLogger(__name__)


def run_agent_cycle():
    db = SessionLocal()

    try:
        logger.info("🔄 Agent cycle started")

        # ✅ Use enum values — Postgres will match correctly
        active_statuses = [
            ReportStatus.PENDING,
            ReportStatus.VERIFIED,
            ReportStatus.IN_PROGRESS,
            ReportStatus.REVIEW_NEEDED,
            ReportStatus.TODO,
        ]

        reports = db.query(Report).filter(
            Report.status.in_(active_statuses)
        ).all()

        logger.info(f"📦 Found {len(reports)} active reports")

        for report in reports:

            if not acquire_lock(report.id):
                logger.warning(f"⚠️ Skipping locked report {report.id}")
                continue

            try:
                action = decide_action(report)
                logger.info(f"🤖 Report {report.id} ({report.status}) → {action['action']}")
                execute_action(db, report, action)

            except Exception as e:
                logger.error(f"❌ Error processing report {report.id}: {e}", exc_info=True)

            finally:
                release_lock(report.id)

        check_auto_close(db)  
        
        db.commit()
        logger.info("✅ Agent cycle completed")

    except Exception as e:
        logger.error(f"❌ Agent cycle failed: {e}", exc_info=True)
        db.rollback()

    finally:
        db.close()