import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler

from agents.complaint_agent import run_agent_cycle
from utils.render_keepalive import run_keepalive_ping

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

    ping_base = (os.getenv("SELF_PING_BASE_URL") or "").strip()
    if ping_base:
        interval = int(os.getenv("SELF_PING_INTERVAL_MINUTES", "12"))
        scheduler.add_job(
            run_keepalive_ping,
            "interval",
            minutes=max(5, interval),
            id="render_keepalive_ping",
            replace_existing=True,
            max_instances=1,
            jitter=90,
        )
        logger.info(
            "Keepalive self-ping enabled every ~%s min (base=%s)",
            max(5, interval),
            ping_base.rstrip("/"),
        )

    scheduler.start()
    job_started = True