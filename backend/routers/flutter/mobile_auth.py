# backendMain/routers/flutter/mobile_auth.py
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
import json
import logging
from db.database import SessionLocal
from model.users import User
from model.user_profile import UserProfile
from model.report import Report, ReportInteraction, IssueCategory, InteractionType, ReportStatus
from utils.auth_utils import get_current_user, get_db
from utils.layer_orchestrator import LayerOrchestrator
from utils.image_storage import ImageStorage

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
    🤖 AI-POWERED REPORT CREATION
    
    This endpoint runs reports through an automated AI Agent that:
    1. Validates image quality (blur, brightness, resolution, etc.)
    2. Classifies the issue using deep learning (pothole/garbage)
    3. Estimates severity (small/medium/large)
    4. Verifies GPS location (detects spoofing)
    5. Automatically accepts or rejects based on results
    
    Flow:
    - User uploads → Temp storage → AI Agent → Cloudinary → Database → Success
    - If AI rejects → Temp deleted → Error returned → User gets immediate feedback
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
        
        # ==========================================
        # STEP 2: SAVE IMAGE TO TEMP STORAGE
        # ==========================================
        logger.info(f"📁 Saving temp image: {image.filename}")
        temp_image_path = image_storage.save_temp(image)
        
        # ==========================================
        # STEP 3: RUN THROUGH AI AGENT
        # ==========================================
        logger.info("🤖 Processing through AI Agent...")
        processing_result = layer_orchestrator.process_report(
            image_path=temp_image_path,
            latitude=location_lat,
            longitude=location_lng
        )
        
        # ==========================================
        # STEP 4: CHECK IF AI AGENT REJECTED
        # ==========================================
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
        
        # Check if AI detected a valid civic issue
        if ai_category not in ["POTHOLE", "GARBAGE"]:
            raise HTTPException(
                status_code=400,
                detail=f"AI could not identify a civic issue. Detected: {ai_category}"
            )
        
        # Check if confidence is acceptable
        if ai_result['confidence'] < 50.0:
            raise HTTPException(
                status_code=400,
                detail=f"AI confidence too low ({ai_result['confidence']:.1f}%). "
                       "The issue is not clearly visible. Please retake the photo with better clarity."
            )
        
        # ==========================================
        # STEP 6: SAVE TO PERMANENT LOCAL STORAGE
        # ==========================================
        logger.info("💾 Saving to permanent local storage...")
        image_relative_path = image_storage.save_permanent(temp_image_path)
        
        # ==========================================
        # STEP 7: CREATE DATABASE RECORD
        # ==========================================
        logger.info("💾 Creating database record with AI results...")
        
        # Use AI-detected category (no user selection)
        issue_category = IssueCategory.POTHOLE if ai_category == "POTHOLE" else IssueCategory.TRASH
        
        # Update title to include AI-detected category
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
            image_url=image_relative_path,
            
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
            
            # Set initial status based on final score
            status=ReportStatus.VERIFIED if ai_result['final_score'] >= 80 else ReportStatus.PENDING
        )
        
        db.add(report)
        
        # ==========================================
        # STEP 8: UPDATE USER STATS
        # ==========================================
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
        if profile:
            profile.total_reported = (profile.total_reported or 0) + 1
        
        db.commit()
        db.refresh(report)
        
        logger.info(f"✅ Report created successfully: ID={report.id}, Score={ai_result['final_score']:.1f}/100")
        
        # ==========================================
        # STEP 9: RETURN SUCCESS WITH AI RESULTS
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
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"❌ Report creation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Server error during report processing: {str(e)}"
        )
    
    finally:
        # ==========================================
        # STEP 10: CLEANUP TEMP FILE (ALWAYS)
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