# backend/agents/agent_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from agents.complaint_agent import run_agent_cycle
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def start_scheduler():
    logger.info("🚀 Agent Scheduler Started")

    scheduler.add_job(
        run_agent_cycle,
        "interval",
        minutes=1,
        id="complaint_agent_job",
        replace_existing=True
    )

    scheduler.start()