from apscheduler.schedulers.background import BackgroundScheduler
from agents.complaint_agent import run_agent_cycle
import logging
import threading

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
job_started = False


def start_scheduler():
    global job_started

    if job_started:
        logger.warning("⚠️ Scheduler already running — skipping duplicate start")
        return

    logger.info("🚀 Agent Scheduler Started (SAFE MODE)")

    scheduler.add_job(
        run_agent_cycle,
        "interval",
        minutes=15,   # production doc
        id="complaint_agent_job",
        replace_existing=True,
        max_instances=1
    )

    scheduler.start()
    job_started = True