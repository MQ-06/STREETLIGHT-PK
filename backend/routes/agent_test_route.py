#routes/agent-test-route.py

from fastapi import APIRouter, Depends, HTTPException, status

from agents.complaint_agent import run_agent_cycle
from model.users import User
from utils.auth_utils import get_current_user

router = APIRouter()


@router.get("/test-agent")
def test_agent(current_user: User = Depends(get_current_user)):
    """Runs one complaint-agent cycle — super_admin only (avoid open trigger in prod)."""
    if (current_user.role or "").strip().lower() != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super_admin may trigger the agent manually",
        )
    run_agent_cycle()
    return {"message": "Agent executed"}