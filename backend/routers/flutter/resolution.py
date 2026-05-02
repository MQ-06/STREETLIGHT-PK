# backend/routers/flutter/resolution.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from model.users import User
from utils.auth_utils import get_current_user, get_db
from agents.resolution_agent import citizen_confirm_resolution

router = APIRouter(prefix="/reports", tags=["Resolution"])


class ConfirmBody(BaseModel):
    confirmed: bool   # True = issue fixed, False = not fixed


@router.post("/{report_id}/confirm-resolution")
def confirm_resolution(
    report_id: int,
    body: ConfirmBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Citizen taps 'Confirm Fixed' or 'Not Fixed' in Flutter app.
    """
    result = citizen_confirm_resolution(
        report_id = report_id,
        user_id   = current_user.id,
        confirmed = body.confirmed,
    )
    return result