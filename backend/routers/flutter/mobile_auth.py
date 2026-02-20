# backendMain/routers/flutter/mobile_auth.py
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional

from db.database import SessionLocal
from model.users import User
from model.user_profile import UserProfile
from model.report import Report, ReportInteraction, IssueCategory, InteractionType, ReportStatus
from utils.auth_utils import get_current_user, get_db
router = APIRouter(prefix="/reports", tags=["Reports"])


def _report_to_dict(report: Report, current_user_id: int, db: Session) -> dict:
    has_supported = db.query(ReportInteraction).filter(
        and_(
            ReportInteraction.report_id == report.id,
            ReportInteraction.user_id == current_user_id,
            ReportInteraction.interaction_type == InteractionType.SUPPORT,
        )
    ).first() is not None

    has_verified = db.query(ReportInteraction).filter(
        and_(
            ReportInteraction.report_id == report.id,
            ReportInteraction.user_id == current_user_id,
            ReportInteraction.interaction_type == InteractionType.VERIFY,
        )
    ).first() is not None

    reporter = report.reporter
    reporter_profile = db.query(UserProfile).filter(
        UserProfile.user_id == reporter.id
    ).first()

    full_name = f"{reporter.first_name} {reporter.last_name}"
    initials = f"{reporter.first_name[0]}{reporter.last_name[0]}".upper()

    return {
        "id": report.id,
        "reporter_id": reporter.id,
        "reporter_name": full_name,
        "reporter_initials": initials,
        "reporter_avatar_url": reporter_profile.profile_image_url if reporter_profile else None,
        "timestamp": report.created_at.isoformat(),
        "location": report.location_address,
        "location_city": report.location_city or "",
        "issue_category": report.category.value,
        "title": report.title,
        "description": report.description,
        "image_url": report.image_url or "",   # empty string if no image yet
        "views": report.views,
        "support_count": report.support_count,
        "verify_count": report.verify_count,
        "status": report.status.value,
        "has_supported": has_supported,
        "has_verified": has_verified,
    }


@router.post("/create")
async def create_report(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location_address: str = Form(...),
    location_city: Optional[str] = Form(None),
    location_lat: Optional[float] = Form(None),
    location_lng: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new report. No image for now — image_url stays null.
    Image will be attached later after AI processing.
    """
    try:
        issue_category = IssueCategory(category.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{category}'. Valid: POTHOLE, TRASH, STREETLIGHT, FLOODING, OTHER"
        )

    report = Report(
        user_id=current_user.id,
        title=title.strip(),
        description=description.strip(),
        category=issue_category,
        location_address=location_address.strip(),
        location_city=location_city,
        location_lat=location_lat,
        location_lng=location_lng,
        image_url=None,  # filled later by AI pipeline
    )
    db.add(report)

    # Increment user's total_reported count
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    if profile:
        profile.total_reported = (profile.total_reported or 0) + 1

    db.commit()
    db.refresh(report)

    return {
        "success": True,
        "message": "Report submitted successfully",
        "report": _report_to_dict(report, current_user.id, db),
    }



@router.get("/feed")
def get_feed(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns paginated reports newest first. Optional category filter."""
    query = db.query(Report)

    if category:
        try:
            cat = IssueCategory(category.upper())
            query = query.filter(Report.category == cat)
        except ValueError:
            pass  # invalid filter → return all

    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    for report in reports:
        report.views = (report.views or 0) + 1
    db.commit()

    return {
        "success": True,
        "count": len(reports),
        "reports": [_report_to_dict(r, current_user.id, db) for r in reports],
    }


# ─────────────────────────────────────────────
# POST /reports/{report_id}/support
# ─────────────────────────────────────────────
@router.post("/{report_id}/support")
def toggle_support(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle support on a report. Calling twice removes support."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    existing = db.query(ReportInteraction).filter(
        and_(
            ReportInteraction.report_id == report_id,
            ReportInteraction.user_id == current_user.id,
            ReportInteraction.interaction_type == InteractionType.SUPPORT,
        )
    ).first()

    if existing:
        db.delete(existing)
        report.support_count = max(0, report.support_count - 1)
        has_supported = False
    else:
        db.add(ReportInteraction(
            report_id=report_id,
            user_id=current_user.id,
            interaction_type=InteractionType.SUPPORT,
        ))
        report.support_count = (report.support_count or 0) + 1
        has_supported = True

    db.commit()
    return {
        "success": True,
        "has_supported": has_supported,
        "support_count": report.support_count,
    }


@router.post("/{report_id}/verify")
def toggle_verify(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle verify on a report. At 5 verifications, status → VERIFIED."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    existing = db.query(ReportInteraction).filter(
        and_(
            ReportInteraction.report_id == report_id,
            ReportInteraction.user_id == current_user.id,
            ReportInteraction.interaction_type == InteractionType.VERIFY,
        )
    ).first()

    if existing:
        db.delete(existing)
        report.verify_count = max(0, report.verify_count - 1)
        has_verified = False
    else:
        db.add(ReportInteraction(
            report_id=report_id,
            user_id=current_user.id,
            interaction_type=InteractionType.VERIFY,
        ))
        report.verify_count = (report.verify_count or 0) + 1
        has_verified = True

        # Auto-promote: 5+ verifications → VERIFIED status
        if report.verify_count >= 5 and report.status == ReportStatus.REPORTED:
            report.status = ReportStatus.VERIFIED

    db.commit()
    return {
        "success": True,
        "has_verified": has_verified,
        "verify_count": report.verify_count,
    }



@router.get("/my")
def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns all reports submitted by the logged-in user."""
    reports = db.query(Report).filter(
        Report.user_id == current_user.id
    ).order_by(Report.created_at.desc()).all()

    return {
        "success": True,
        "count": len(reports),
        "reports": [_report_to_dict(r, current_user.id, db) for r in reports],
    }