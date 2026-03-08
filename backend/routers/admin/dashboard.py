from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import SessionLocal
from model.report import Report
from model.users import User
from utils.rbac import require_roles

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/overview")
def dashboard_overview(
    current_user: User = Depends(
        require_roles(
            "municipal_officer",
            "department_head",
            "city_planner",
            "system_admin",
        )
    ),
    db: Session = Depends(get_db),
):
    reports = db.query(Report).all()
    status_counts = Counter([(r.status.value if r.status else "UNKNOWN") for r in reports])

    return {
        "viewer_role": current_user.role,
        "totals": {
            "reports": len(reports),
            "pending": status_counts.get("PENDING", 0),
            "verified": status_counts.get("VERIFIED", 0),
            "in_progress": status_counts.get("IN_PROGRESS", 0),
            "resolved": status_counts.get("RESOLVED", 0),
        },
    }
