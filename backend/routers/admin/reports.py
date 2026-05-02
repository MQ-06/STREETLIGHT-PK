# backend/routers/admin/reports.py
import logging
import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload

from db.database import SessionLocal
from model.report import Report, KanbanStage, ReportStatus
from model.report_logs import ReportLog
from model.users import User
from utils.rbac import require_roles

import cloudinary
import cloudinary.uploader
import tempfile
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/reports", tags=["Admin Reports"])


def _search_reports_clause(search: str):
    """Match complaint id (#SR-0042, SR42, 42), title, location text, city, department."""
    s = search.strip()
    if not s:
        return None
    m = re.match(r"^#?SR-?(\d+)$", s, re.IGNORECASE)
    if m:
        return Report.id == int(m.group(1))
    if s.isdigit():
        return Report.id == int(s)
    pat = f"%{s}%"
    return or_(
        Report.title.ilike(pat),
        Report.location_address.ilike(pat),
        Report.location_city.ilike(pat),
        Report.assigned_department.ilike(pat),
        Report.assigned_city.ilike(pat),
    )

ALL_ADMIN = require_roles(
    "super_admin",
    "city_admin",
    "dept_officer",
    "municipal_officer",
    "department_head",
    "city_planner",
    "system_admin",
)

CATEGORY_ICON = {"POTHOLE": "🕳️", "TRASH": "🗑️"}

STAGE_ORDER = [
    KanbanStage.NEW,
    KanbanStage.PENDING_VERIFICATION,
    KanbanStage.VERIFIED,
    KanbanStage.IN_PROGRESS,
    KanbanStage.AWAITING_FEEDBACK,
    KanbanStage.RESOLVED,
    KanbanStage.CLOSED,
]

KANBAN_STAGE_KEYS = [s.value for s in STAGE_ORDER]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _base_query(db: Session, user: User, eager_reporter: bool = False):
    role = (user.role or "").lower()
    q = db.query(Report)
    if eager_reporter:
        q = q.options(joinedload(Report.reporter))

    if role == "dept_officer":
        routing = (
            db.query(
                __import__(
                    "model.routing_table", fromlist=["RoutingTable"]
                ).RoutingTable
            )
            .filter_by(officer_id=user.id, is_active=True)
            .first()
        )
        if routing:
            q = q.filter(
                Report.assigned_city == routing.city,
                Report.assigned_department == routing.department,
            )

    elif role == "city_admin":
        if user.city:
            q = q.filter(Report.assigned_city == user.city)

    return q


def _report_summary(r: Report) -> dict:
    severity_colors = {
        "large": ("#fef2f2", "#ef4444"),
        "medium": ("#fff7ed", "#f97316"),
        "small": ("#f0fdf4", "#22c55e"),
    }

    sev = (r.ai_severity or "medium").lower()
    sev_bg, sev_color = severity_colors.get(sev, ("#fff7ed", "#f97316"))

    stage_dots = {
        "NEW": "#3b82f6",
        "PENDING_VERIFICATION": "#f97316",
        "VERIFIED": "#f97316",
        "IN_PROGRESS": "#f97316",
        "AWAITING_FEEDBACK": "#8b5cf6",
        "RESOLVED": "#22c55e",
        "CLOSED": "#64748b",
    }

    stage_val = r.kanban_stage.value if r.kanban_stage else "NEW"

    return {
        "id": r.id,
        "display_id": f"#SR-{r.id:04d}",
        "title": r.title,
        "description": r.description,
        "category": r.category.value if r.category else None,
        "icon": CATEGORY_ICON.get(r.category.value if r.category else "", "📋"),
        "location": r.location_address,
        "location_city": r.location_city or r.assigned_city,
        "lat": r.location_lat,
        "lng": r.location_lng,
        "image_url": r.image_url,
        "status": r.status.value if r.status else None,
        "kanban_stage": stage_val,
        "stage_dot": stage_dots.get(stage_val, "#9ca3af"),
        "severity": (r.ai_severity or "medium").capitalize(),
        "severity_bg": sev_bg,
        "severity_color": sev_color,
        "ai_confidence": r.ai_confidence,
        "combined_score": r.combined_score,
        "assigned_city": r.assigned_city,
        "assigned_department": r.assigned_department,
        "assigned_officer_id": r.assigned_officer_id,
        "assigned_at": r.assigned_at.isoformat() if r.assigned_at else None,
        "reporter_name": (
            f"{r.reporter.first_name} {r.reporter.last_name}"
            if r.reporter
            else "Unknown"
        ),
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "is_flagged_for_spam": r.is_flagged_for_spam,
    }


# ── GET /admin/reports ─────────────────────────


@router.get("")
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=500),
    stage: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    q = _base_query(db, current_user, eager_reporter=True)

    if stage:
        try:
            q = q.filter(Report.kanban_stage == KanbanStage(stage.upper()))
        except ValueError:
            pass

    if category:
        q = q.filter(Report.category.ilike(f"%{category}%"))

    if city:
        q = q.filter(Report.assigned_city == city.lower())

    clause = _search_reports_clause(search) if search else None
    if clause is not None:
        q = q.filter(clause)

    if date_from:
        try:
            from datetime import datetime as dt

            q = q.filter(Report.created_at >= dt.fromisoformat(date_from))
        except ValueError:
            pass

    total = q.count()
    reports = q.order_by(desc(Report.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "reports": [_report_summary(r) for r in reports],
    }


# ── GET /admin/reports/kanban ───────────────────────────────────────────────


@router.get("/kanban")
def kanban_reports(
    search: Optional[str] = Query(None),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    """Kanban columns for Resolution Board (card shape matches list summary)."""
    q = _base_query(db, current_user, eager_reporter=True)
    clause = _search_reports_clause(search) if search else None
    if clause is not None:
        q = q.filter(clause)
    reports = q.order_by(desc(Report.created_at)).limit(500).all()

    buckets: dict[str, list] = {k: [] for k in KANBAN_STAGE_KEYS}
    for r in reports:
        key = r.kanban_stage.value if r.kanban_stage else "NEW"
        if key not in buckets:
            key = "NEW"
        buckets[key].append(_report_summary(r))

    columns = [{"stage": k, "cards": buckets[k]} for k in KANBAN_STAGE_KEYS]
    return {"columns": columns}


# ── GET /admin/reports/{id} ──────────────────────────────────────────────────


@router.get("/{report_id}")
def get_report_detail(
    report_id: int,
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    """Single report with audit trail for Complaint Detail page."""
    q = _base_query(db, current_user, eager_reporter=True)
    report = q.filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    logs = (
        db.query(ReportLog)
        .filter(ReportLog.report_id == report_id)
        .order_by(desc(ReportLog.created_at))
        .all()
    )

    data = _report_summary(report)
    data["logs"] = [
        {
            "id": log.id,
            "changed_by": log.changed_by,
            "previous_stage": log.previous_stage,
            "new_stage": log.new_stage,
            "previous_status": log.previous_status,
            "new_status": log.new_status,
            "note": log.note,
            "ai_managed": log.ai_managed,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
    data["trust_score"] = report.trust_score
    data["gps_verified"] = bool(report.gps_verified)
    data["after_image_url"] = report.after_image_url
    data["citizen_response"] = report.citizen_response
    return data


# ── POST /admin/reports/{id}/note ─────────────────────────


class NoteBody(BaseModel):
    note: str


@router.post("/{report_id}/note")
def add_note(
    report_id: int,
    body: NoteBody,
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    q = _base_query(db, current_user)
    report = q.filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not body.note.strip():
        raise HTTPException(status_code=400, detail="Note cannot be empty")

    log = ReportLog(
        report_id=report.id,
        changed_by=str(current_user.id),
        note=body.note.strip(),
        ai_managed=False,
    )
    db.add(log)
    db.commit()

    logger.info(f"Note added to report {report_id} by user {current_user.id}")
    return {"success": True}


# ── POST /admin/reports/{id}/after-image ─────────────────────────


@router.post("/{report_id}/after-image")
async def upload_after_image(
    report_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    q = _base_query(db, current_user)
    report = q.filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.kanban_stage not in [KanbanStage.IN_PROGRESS, KanbanStage.VERIFIED]:
        raise HTTPException(
            status_code=400,
            detail=f"After-image can only be uploaded when report is IN_PROGRESS or VERIFIED. Current: {report.kanban_stage}",
        )

    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        upload_result = cloudinary.uploader.upload(
            tmp_path,
            folder="streetlight/after_images",
            public_id=f"after_{report_id}_{int(datetime.now(timezone.utc).timestamp())}",
        )
        after_image_url = upload_result["secure_url"]
        os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"❌ Cloudinary upload failed: {e}")
        raise HTTPException(status_code=500, detail="Image upload failed")

    report.after_image_url = after_image_url
    report.after_image_uploaded_at = datetime.now(timezone.utc)
    report.after_image_uploaded_by = current_user.id
    report.kanban_stage = KanbanStage.AWAITING_FEEDBACK

    log = ReportLog(
        report_id=report.id,
        changed_by=str(current_user.id),
        previous_stage=KanbanStage.IN_PROGRESS.value,
        new_stage=KanbanStage.AWAITING_FEEDBACK.value,
        note=f"After-image uploaded by officer {current_user.id}. Pending AI verification.",
        ai_managed=False,
    )

    db.add(log)
    db.commit()
    db.refresh(report)

    from agents.resolution_agent import process_after_image
    import threading

    threading.Thread(target=process_after_image, args=(report_id,), daemon=True).start()

    return {
        "success": True,
        "after_image_url": after_image_url,
        "stage": KanbanStage.AWAITING_FEEDBACK.value,
        "message": "After-image uploaded. AI verification in progress.",
    }

    # ── PATCH /admin/reports/{id}/stage ───────────────────────────────────────


class StageUpdate(BaseModel):
    stage: str
    note: Optional[str] = None


@router.patch("/{report_id}/stage")
def update_stage(
    report_id: int,
    body: StageUpdate,
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    q = _base_query(db, current_user)
    report = q.filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        new_stage = KanbanStage(body.stage.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {body.stage}")

    prev_stage = report.kanban_stage.value if report.kanban_stage else None
    report.kanban_stage = new_stage

    # Sync ReportStatus
    if new_stage == KanbanStage.IN_PROGRESS:
        report.status = ReportStatus.IN_PROGRESS
    elif new_stage == KanbanStage.VERIFIED:
        report.status = ReportStatus.VERIFIED

    note = body.note or f"Stage changed to {new_stage.value}"
    log = ReportLog(
        report_id=report.id,
        changed_by=str(current_user.id),
        previous_stage=prev_stage,
        new_stage=new_stage.value,
        note=note,
        ai_managed=False,
    )
    db.add(log)
    db.commit()
    db.refresh(report)

    logger.info(
        f"Stage update: report {report_id} → {new_stage.value} by user {current_user.id}"
    )

    # ── RESOLUTION TRIGGER ─────────────────────────────────────────────────
    if new_stage == KanbanStage.RESOLVED:
        from agents.resolution_agent import process_resolution
        import threading

        threading.Thread(
            target=process_resolution, args=(report.id,), daemon=True
        ).start()
        logger.info(f"🤖 Resolution agent triggered for report #{report_id}")

    return {"success": True, "stage": new_stage.value, "note": note}
