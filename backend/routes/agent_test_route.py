#routes/agent-test-route.py
from fastapi import APIRouter
from agents.complaint_agent import run_agent_cycle

router = APIRouter()

@router.get("/test-agent")
def test_agent():
    run_agent_cycle()
    return {"message": "Agent executed"}