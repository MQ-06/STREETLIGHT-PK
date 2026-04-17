# backend/agents/complaint_agent.py

from db.database import SessionLocal
from model.report import Report
from agents.agent_rules import decide_action
from agents.agent_tools import execute_action
import logging

logger = logging.getLogger(__name__)


def run_agent_cycle():
    db = SessionLocal()

    try:
        logger.info("🔄 Agent cycle started")

        # 1. Observe
        reports = db.query(Report).filter(
            Report.status.in_([
                "PENDING",
                "VERIFIED",
                "IN_PROGRESS",
                "AWAITING_FEEDBACK"
            ])
        ).all()

        logger.info(f"📦 Found {len(reports)} active reports")

        # 2. Process each report
        for report in reports:

            try:
                # 3. Reason
                action = decide_action(report)

                # 4. Act
                execute_action(db, report, action)

            except Exception as e:
                logger.error(f"❌ Error processing report {report.id}: {e}")

        db.commit()
        logger.info("✅ Agent cycle completed")

    finally:
        db.close()