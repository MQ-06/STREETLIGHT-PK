# backend/agents/agent_runner.py

from agents.agent_scheduler import start_scheduler
import time

if __name__ == "__main__":
    start_scheduler()

    while True:
        time.sleep(60)