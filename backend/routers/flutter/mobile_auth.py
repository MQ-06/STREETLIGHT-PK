# backendMain/routers/flutter/mobile_auth.py
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
import json
import logging
from datetime import datetime, timezone
from db.database import SessionLocal
from model.users import User
from model.user_profile import UserProfile
from model.report import Report, ReportInteraction, IssueCategory, InteractionType, ReportStatus
from utils.auth_utils import get_current_user, get_db
from utils.layer_orchestrator import LayerOrchestrator
from utils.image_storage import ImageStorage
from ai_layers.layer2_fraud_detection.fraud_engine import FraudDetector

# Configure logging
logger = logging.getLogger(__name__)

# Initialize AI Agent and Image Storage (once at module level)
logger.info("Initializing AI Agent for report processing...")
layer_orchestrator = LayerOrchestrator()
image_storage = ImageStorage()
logger.info("AI Agent ready to process reports")

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
    image: UploadFile = File(...),  # REQUIRED: Image file for AI processing
    title: str = Form(...),
    description: Optional[str] = Form(None),
    location_address: str = Form(...),
    location_city: Optional[str] = Form(None),
    location_lat: Optional[float] = Form(None),
    location_lng: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🤖 AI-POWERED REPORT CREATION  (Layer 0 → Layer 1 → Layer 2 → Cloudinary → DB)

    Automated pipeline:
    1. Validate GPS coordinates
    2. Save image to temp storage
    3. Layer 0: Image quality validation
    4. Layer 1: AI classification + GPS verification
    5. Layer 2: Fraud detection (spoofing / duplicate / spam)
    6. Upload to Cloudinary (only if all hard blocks pass)
    7. Persist to database
    """
    temp_image_path = None

    try:
        logger.info(f"📥 New report submission from user {current_user.id}")

        # ==========================================
        # STEP 1: VALIDATE GPS COORDINATES
        # ==========================================
        if location_lat is None or location_lng is None:
            raise HTTPException(
                status_code=400,
                detail="GPS coordinates are required for report submission"
            )

        # Capture submission timestamp once — used by fraud checks
        submitted_at = datetime.now(timezone.utc)

        # ==========================================
        # STEP 2: SAVE IMAGE TO TEMP STORAGE
        # ==========================================
        logger.info(f"📁 Saving temp image: {image.filename}")
        temp_image_path = image_storage.save_temp(image)

        # ==========================================
        # STEP 3 & 4: RUN THROUGH AI AGENT (Layer 0 + Layer 1)
        # ==========================================
        logger.info("🤖 Processing through AI Agent (Layer 0 + Layer 1)...")
        processing_result = layer_orchestrator.process_report(
            image_path=temp_image_path,
            latitude=location_lat,
            longitude=location_lng
        )

        if not processing_result['passed']:
            logger.warning(f"❌ AI Agent rejected report: {processing_result['errors']}")
            raise HTTPException(
                status_code=400,
                detail={
                    'message': 'Report validation failed',
                    'errors': processing_result['errors'],
                    'warnings': processing_result['warnings'],
                    'agent_decision': processing_result['agent_decision'],
                    'agent_reason': processing_result['agent_reason']
                }
            )

        # ==========================================
        # STEP 5: VALIDATE AI DETECTED CATEGORY
        # ==========================================
        ai_result = processing_result['layer1']
        ai_category = ai_result['predicted_class'].upper()

        if ai_category not in ["POTHOLE", "GARBAGE"]:
            raise HTTPException(
                status_code=400,
                detail=f"AI could not identify a civic issue. Detected: {ai_category}"
            )

        if ai_result['confidence'] < 50.0:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"AI confidence too low ({ai_result['confidence']:.1f}%). "
                    "The issue is not clearly visible. Please retake the photo with better clarity."
                )
            )

        issue_category = IssueCategory.POTHOLE if ai_category == "POTHOLE" else IssueCategory.TRASH

        # ==========================================
        # STEP 6: LAYER 2 — FRAUD DETECTION (Engine B)
        # Runs AFTER Layer 1, BEFORE Cloudinary upload.
        # ==========================================
        logger.info("🛡️ Running Layer 2: Fraud Detection...")
        fraud_result = FraudDetector(db).run_all_checks(
            user_id=current_user.id,
            category=issue_category,
            lat=location_lat,
            lng=location_lng,
            submitted_at=submitted_at,
        )

        # ── 6a: GPS Spoofing → immediate hard block + reputation penalty ──
        if fraud_result['is_spoofed']:
            logger.warning(
                f"🚨 BLOCKED (spoofing): user={current_user.id} "
                f"GPS=({location_lat}, {location_lng})"
            )

            # Apply -50 point penalty to user's impact score
            profile = db.query(UserProfile).filter(
                UserProfile.user_id == current_user.id
            ).first()
            if profile:
                profile.impact_score = (profile.impact_score or 0) - 50
                db.commit()
                logger.warning(
                    f"📉 Penalty applied: -50 points to user={current_user.id} "
                    f"(new impact_score={profile.impact_score})"
                )

            raise HTTPException(
                status_code=400,
                detail={
                    'message': (
                        "GPS spoofing detected. Your location jumped an impossible distance "
                        "in under 2 minutes. Please ensure your GPS is accurate and try again."
                    ),
                    'fraud_type': 'GPS_SPOOFING',
                    'penalty_applied': -50,
                }
            )

        # ── 6b: Duplicate report → soft link (save & link to original) ─────
        duplicate_of_id = fraud_result['duplicate_of_id']
        duplicate_report = fraud_result['duplicate_report']
        if duplicate_of_id is not None:
            logger.info(
                f"📋 Duplicate detected: user={current_user.id} "
                f"→ will be linked to original report ID={duplicate_of_id}"
            )

        # ── 6c: Spam flag → soft flag; continue pipeline ──────────────────
        is_flagged_for_spam = fraud_result['is_spam']
        if is_flagged_for_spam:
            logger.warning(
                f"⚠️ Spam flag set for user={current_user.id} "
                f"({fraud_result['hourly_count']} reports in last hour) — "
                "report will be saved and queued for admin review"
            )

        # ==========================================
        # STEP 7: UPLOAD TO CLOUDINARY
        # (Only reached if no hard block was raised above)
        # ==========================================
        category_str = "pothole_img" if ai_category == "POTHOLE" else "garbage_img"
        logger.info(f"☁️ Uploading to Cloudinary folder: {category_str}...")
        image_url = image_storage.upload_to_cloudinary(temp_image_path, category=category_str)

        # ==========================================
        # STEP 8: CREATE DATABASE RECORD
        # ==========================================
        logger.info("💾 Creating database record with AI + Fraud Detection results...")

        ai_category_name = "Pothole" if ai_category == "POTHOLE" else "Garbage"
        updated_title = title.replace("Civic Issue", ai_category_name)

        report = Report(
            user_id=current_user.id,
            title=updated_title.strip(),
            description=(description or "").strip(),
            category=issue_category,
            location_address=location_address.strip(),
            location_city=location_city,
            location_lat=location_lat,
            location_lng=location_lng,
            image_url=image_url,

            # Layer 0: Validation results
            validation_score=processing_result['layer0']['overall_quality'],
            validation_status='passed',
            validation_warnings=json.dumps(processing_result['layer0']['warnings']),

            # Layer 1: AI results
            ai_confidence=ai_result['confidence'],
            ai_predicted_class=ai_result['predicted_class'],
            ai_severity=ai_result['severity'],
            final_score=ai_result['final_score'],

            # GPS verification
            gps_verified=(ai_result['gps_verification']['verification_status'] == 'verified'),
            gps_has_photo_location=ai_result['gps_verification']['has_photo_gps'],
            gps_distance_km=ai_result['gps_verification'].get('distance_km'),
            gps_spoofing_detected=ai_result['gps_verification']['is_spoofed'],

            # Layer 2: Fraud Detection results
            is_flagged_for_spam=is_flagged_for_spam,
            duplicate_of_id=duplicate_of_id,

            # Initial status based on final score
            status=ReportStatus.VERIFIED if ai_result['final_score'] >= 80 else ReportStatus.PENDING
        )

        db.add(report)

        # ==========================================
        # STEP 9: UPDATE USER STATS
        # ==========================================
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
        if profile:
            profile.total_reported = (profile.total_reported or 0) + 1

        db.commit()
        db.refresh(report)

        logger.info(
            f"✅ Report created: ID={report.id} | Score={ai_result['final_score']:.1f}/100 "
            f"| spam_flag={is_flagged_for_spam}"
        )

        # ==========================================
        # STEP 10: RETURN SUCCESS
        # ==========================================
        return {
            'success': True,
            'message': ai_result['message'],
            'report': _report_to_dict(report, current_user.id, db),
            'ai_results': {
                'confidence': ai_result['confidence'],
                'severity': ai_result['severity'],
                'final_score': ai_result['final_score'],
                'gps_verification': {
                    'status': ai_result['gps_verification']['verification_status'],
                    'distance_km': ai_result['gps_verification'].get('distance_km'),
                    'is_spoofed': ai_result['gps_verification']['is_spoofed']
                }
            },
            'validation': {
                'quality_score': processing_result['layer0']['overall_quality'],
                'warnings': processing_result['warnings']
            },
            'fraud_check': {
                'is_flagged_for_spam': is_flagged_for_spam,
                'hourly_count': fraud_result['hourly_count'],
                'is_duplicate': duplicate_of_id is not None,
                'duplicate_of_id': duplicate_of_id,
                'existing_report': duplicate_report,
            }
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is (includes all fraud blocks above)
        raise

    except Exception as e:
        logger.error(f"❌ Report creation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Server error during report processing: {str(e)}"
        )

    finally:
        # ==========================================
        # STEP 11: CLEANUP TEMP FILE (ALWAYS)
        # Runs even when an exception is raised — ensures no orphaned temp files.
        # ==========================================
        if temp_image_path:
            image_storage.cleanup_temp(temp_image_path)



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