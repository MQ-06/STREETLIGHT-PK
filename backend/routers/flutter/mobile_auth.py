# backendMain/routers/flutter/mobile_auth.py
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from typing import Optional
import json
import logging
from datetime import datetime, timezone
from db.database import SessionLocal
from model.users import User
from model.user_profile import UserProfile
from model.report import (
    Report,
    ReportInteraction,
    Comment,
    IssueCategory,
    InteractionType,
    ReportStatus,
    ReportContribution,
)
from utils.auth_utils import get_current_user, get_db
from utils.layer_orchestrator import LayerOrchestrator
from utils.image_storage import ImageStorage
from ai_layers.layer2_fraud_detection.fraud_engine import FraudDetector
from ai_layers.layer3_community_verification.community_engine import CommunityVerificationEngine
from ai_layers.layer4_trust_history import TrustHistoryEngine
from ai_layers.layer5_final_score import FinalScoreCalculator
import piexif
from utils.impact_score import (
    ImpactScoreManager,
    PENALTY_SPOOFING,
    PENALTY_SPAM,
    POINTS_REPORT_CREATED,
    POINTS_VOTE_CAST,
)
from services.routing.routing_service import route_report
# Notifications/push are handled at later lifecycle stages (e.g. RESOLVED).

# Configure logging
logger = logging.getLogger(__name__)

# Initialize AI Agent and Image Storage (once at module level)
logger.info("Initializing AI Agent for report processing...")
layer_orchestrator = LayerOrchestrator()
image_storage = ImageStorage()
logger.info("AI Agent ready to process reports")

router = APIRouter(prefix="/reports", tags=["Reports"])


class FcmTokenRequest(BaseModel):
    fcm_token: str


@router.post("/fcm-token")
def update_fcm_token(
    body: FcmTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Store FCM device token for push notifications. Also exposed at /users/fcm-token."""
    try:
        profile = (
            db.query(UserProfile)
            .filter(UserProfile.user_id == current_user.id)
            .first()
        )
        if profile is None:
            raise HTTPException(status_code=404, detail="User profile not found")
        profile.fcm_token = body.fcm_token.strip()
        db.commit()
        logger.info(f"🔔 FCM token updated for user ID={current_user.id}")
        return {"success": True, "message": "FCM token updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ update_fcm_token error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


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

    comment_count = db.query(func.count(Comment.id)).filter(
        Comment.report_id == report.id
    ).scalar() or 0

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
        "confirmation_count": getattr(report, "confirmation_count", 0),
        "comment_count": comment_count,
        "status": report.status.value,
        "combined_score": getattr(report, "combined_score", None),
        "verification_status": getattr(report, "verification_status", None),
        "has_supported": has_supported,
        "has_verified": has_verified,
    }


@router.post("/create")
def create_report(
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

        # Fallback mode (model unavailable): default to GARBAGE for manual review
        if ai_category not in ["POTHOLE", "GARBAGE"]:
            if ai_result.get("fallback_mode"):
                logger.info("📋 Fallback mode: defaulting to GARBAGE for officer review")
                ai_category = "GARBAGE"
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"AI could not identify a civic issue. Detected: {ai_category}"
                )

        issue_category = IssueCategory.POTHOLE if ai_category == "POTHOLE" else IssueCategory.TRASH

        # ==========================================
        # STEP 5.5: HASH-BASED DUPLICATE CHECK (MERGE AS CONTRIBUTION)
        # Note: this is location-agnostic by design — the exact same photo
        # indicates a duplicate report even if the user moves a few metres.
        # ==========================================
        image_hash = ai_result.get("image_hash")
        if image_hash:
            existing_report = (
                db.query(Report)
                .filter(Report.image_hash == image_hash)
                .order_by(Report.created_at.asc())
                .first()
            )
        else:
            existing_report = None

        if existing_report is not None:
            logger.info(
                f"📋 Hash-duplicate detected: user={current_user.id} "
                f"→ will be merged into original report ID={existing_report.id}"
            )

            category_str = "pothole_img" if ai_category == "POTHOLE" else "garbage_img"

            # Strip EXIF GPS data before permanent upload
            try:
                piexif.remove(str(temp_image_path))
            except Exception as ex:
                logger.warning(f"piexif.remove failed (non-blocking): {ex}")

            logger.info(f"☁️ Uploading duplicate image to Cloudinary folder: {category_str}...")
            image_url = image_storage.upload_to_cloudinary(
                temp_image_path, category=category_str
            )

            contribution = ReportContribution(
                report_id=existing_report.id,
                user_id=current_user.id,
                image_url=image_url,
                ai_confidence=ai_result["confidence"],
                ai_severity=ai_result["severity"],
                location_lat=location_lat,
                location_lng=location_lng,
            )
            db.add(contribution)

            existing_report.confirmation_count = (existing_report.confirmation_count or 0) + 1

            # Track the best (highest-confidence) image URL seen so far
            existing_conf = existing_report.ai_confidence or 0.0
            if ai_result["confidence"] > existing_conf:
                existing_report.best_image_url = image_url

            # Community-style auto-verification based on confirmations
            if (
                existing_report.confirmation_count >= 3
                and (existing_report.verify_count or 0) < 5
            ):
                existing_report.verify_count = (existing_report.verify_count or 0) + 1

            if (
                existing_report.confirmation_count >= 5
                and existing_report.status == ReportStatus.PENDING
            ):
                existing_report.status = ReportStatus.VERIFIED

            # Update reporting user's profile stats
            profile = (
                db.query(UserProfile)
                .filter(UserProfile.user_id == current_user.id)
                .first()
            )
            if profile:
                profile.total_reported = (profile.total_reported or 0) + 1
                profile.impact_score = (profile.impact_score or 0) + 5

            db.commit()
            db.refresh(existing_report)

            return {
                "success": True,
                "merged": True,
                "message": (
                    "Your report has been merged with an existing report with the same photo. "
                    "Thank you for confirming this issue!"
                ),
                "original_report_id": existing_report.id,
                "original_report": _report_to_dict(existing_report, current_user.id, db),
                "confirmation_count": existing_report.confirmation_count,
            }

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

            # Apply spoofing penalty via centralized manager
            ImpactScoreManager(db).deduct_points(current_user.id, PENALTY_SPOOFING, "GPS_SPOOFING")

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

        # ── 6b: Engine D — Trust & History Check ─────────────────────────────
        trust_result = {}
        try:
            trust_result = TrustHistoryEngine(db).evaluate_trust(current_user.id)
            logger.info(
                f"🔐 Trust check: score={trust_result.get('trust_score', 'N/A')}, "
                f"trusted={trust_result.get('is_trusted', 'N/A')}"
            )
        except Exception as e:
            logger.error(f"❌ Trust check failed (non-blocking): {e}")
            trust_result = {"trust_score": None, "is_trusted": True}

        # ── 6c: Duplicate report → merge as contribution ─────
        duplicate_of_id = fraud_result['duplicate_of_id']
        duplicate_report = fraud_result['duplicate_report']
        if duplicate_of_id is not None:
            logger.info(
                f"📋 Duplicate detected: user={current_user.id} "
                f"→ will be merged into original report ID={duplicate_of_id}"
            )

            # Upload this confirming image to Cloudinary (after stripping EXIF GPS)
            category_str = "pothole_img" if ai_category == "POTHOLE" else "garbage_img"
            try:
                piexif.remove(str(temp_image_path))
            except Exception as ex:
                logger.warning(f"piexif.remove failed (non-blocking): {ex}")
            logger.info(f"☁️ Uploading duplicate image to Cloudinary folder: {category_str}...")
            image_url = image_storage.upload_to_cloudinary(
                temp_image_path, category=category_str
            )

            # Create a contribution record linked to the original report
            contribution = ReportContribution(
                report_id=duplicate_of_id,
                user_id=current_user.id,
                image_url=image_url,
                ai_confidence=ai_result["confidence"],
                ai_severity=ai_result["severity"],
                location_lat=location_lat,
                location_lng=location_lng,
            )
            db.add(contribution)

            # Fetch original report and update its confirmation stats
            original_report = db.query(Report).filter(Report.id == duplicate_of_id).first()
            if not original_report:
                logger.error(
                    f"Duplicate target report ID={duplicate_of_id} not found; "
                    "cannot merge contribution."
                )
                raise HTTPException(
                    status_code=404,
                    detail="Original report for duplicate merge not found",
                )

            original_report.confirmation_count = (original_report.confirmation_count or 0) + 1

            # Track the best (highest-confidence) image URL seen so far
            existing_conf = original_report.ai_confidence or 0.0
            if ai_result["confidence"] > existing_conf:
                original_report.best_image_url = image_url

            # Community-style auto-verification based on confirmations
            if (
                original_report.confirmation_count >= 3
                and (original_report.verify_count or 0) < 5
            ):
                original_report.verify_count = (original_report.verify_count or 0) + 1

            if (
                original_report.confirmation_count >= 5
                and original_report.status == ReportStatus.PENDING
            ):
                original_report.status = ReportStatus.VERIFIED

            # Update reporting user's profile stats
            profile = (
                db.query(UserProfile)
                .filter(UserProfile.user_id == current_user.id)
                .first()
            )
            if profile:
                profile.total_reported = (profile.total_reported or 0) + 1
                profile.impact_score = (profile.impact_score or 0) + 5

            db.commit()
            db.refresh(original_report)

            return {
                "success": True,
                "merged": True,
                "message": (
                    "Your report has been merged with an existing nearby report. "
                    "Thank you for confirming this issue!"
                ),
                "original_report_id": duplicate_of_id,
                "original_report": _report_to_dict(original_report, current_user.id, db),
                "confirmation_count": original_report.confirmation_count,
            }

        # ── 6d: Spam flag → soft flag; continue pipeline ──────────────────
        is_flagged_for_spam = fraud_result['is_spam']
        if is_flagged_for_spam:
            logger.warning(
                f"⚠️ Spam flag set for user={current_user.id} "
                f"({fraud_result['hourly_count']} reports in last hour) — "
                "report will be saved and queued for admin review"
            )
            ImpactScoreManager(db).deduct_points(current_user.id, PENALTY_SPAM, "SPAM_FLAGGED")

        # ==========================================
        # STEP 7: UPLOAD TO CLOUDINARY
        # (Only reached if no hard block or duplicate-merge path was taken)
        # ==========================================
        category_str = "pothole_img" if ai_category == "POTHOLE" else "garbage_img"
        # Strip EXIF GPS data before permanent upload
        try:
            piexif.remove(str(temp_image_path))
        except Exception as ex:
            logger.warning(f"piexif.remove failed (non-blocking): {ex}")
        logger.info(f"☁️ Uploading to Cloudinary folder: {category_str}...")
        image_url = image_storage.upload_to_cloudinary(
            temp_image_path, category=category_str
        )

        # ==========================================
        # STEP 8: CREATE DATABASE RECORD
        # ==========================================
        logger.info("💾 Creating database record with AI + Fraud Detection results...")

        ai_category_name = "Pothole" if ai_category == "POTHOLE" else "Garbage"
        updated_title = title.replace("Civic Issue", ai_category_name)

        final_score_val = ai_result['final_score']
        # Hard-reject only truly low-quality submissions here; leave lifecycle
        # status to Layer 5 so there is a single source of truth.
        # Skip when in fallback mode (model unavailable) — report goes to manual review
        if not ai_result.get("fallback_mode") and final_score_val < 60:
            raise HTTPException(
                status_code=400,
                detail={
                    'message': (
                        f"Report score too low ({final_score_val:.0f}/100). "
                        "The photo may not clearly show the issue. "
                        "Please try again from closer with better lighting."
                    ),
                    'score': final_score_val,
                    'errors': [
                        f"Score {final_score_val:.0f}/100 is below the minimum threshold of 60."
                    ],
                    'agent_decision': 'REJECTED',
                    'agent_reason': 'Final score below minimum threshold',
                },
            )
        # All accepted reports start as PENDING; Layer 5 will promote/downgrade.
        report_status = ReportStatus.PENDING

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
            image_hash=image_hash,

            # GPS verification
            gps_verified=(ai_result['gps_verification']['verification_status'] == 'verified'),
            gps_has_photo_location=ai_result['gps_verification']['has_photo_gps'],
            gps_distance_km=ai_result['gps_verification'].get('distance_km'),
            gps_spoofing_detected=ai_result['gps_verification']['is_spoofed'],

            # Layer 2: Fraud Detection results
            is_flagged_for_spam=is_flagged_for_spam,
            duplicate_of_id=duplicate_of_id,

            # Layer 4: Trust score snapshot
            trust_score=trust_result.get("trust_score"),
            
            # Initial status based on AI final score buckets
            status=report_status
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

        ImpactScoreManager(db).award_points(current_user.id, POINTS_REPORT_CREATED, "REPORT_CREATED")

        logger.info(
            f"✅ Report created: ID={report.id} | Score={ai_result['final_score']:.1f}/100 "
            f"| spam_flag={is_flagged_for_spam}"
        )

        # ==========================================
        # STEP 8.5: TRIGGER COMMUNITY VERIFICATION (Layer 3)
        # Non-blocking — a failure here must never prevent the report from
        # being returned to the user.  Community verification is optional.
        # ==========================================
        community_verification_created = False
        try:
            CommunityVerificationEngine(db).create_verification_request(
                report_id=report.id,
                lat=location_lat,
                lng=location_lng,
            )
            community_verification_created = True
            logger.info(f"🏘️ Layer 3: verification request created for report ID={report.id}")
        except Exception as layer3_exc:
            logger.warning(
                f"⚠️ Layer 3: verification request failed for report ID={report.id} "
                f"(non-blocking) — {layer3_exc}"
            )

        # ==========================================
        # STEP 9b: CALCULATE FINAL CONFIDENCE SCORE (Layer 5)
        # Non-blocking — runs after report + community verification are persisted.
        # ==========================================
        score_result = {}
        try:
            score_result = FinalScoreCalculator(db).calculate_final_score(report.id)
            logger.info(
                f"📊 Final Score: {score_result.get('combined_score', 'N/A')} → "
                f"{score_result.get('verification_status', 'N/A')}"
            )
        except Exception as e:
            logger.error(f"❌ Final score calculation failed (non-blocking): {e}")
            score_result = {"combined_score": None, "verification_status": "PENDING"}

        # ==========================================
        # STEP 9c: AUTO-ROUTING (Phase 1)
        # Non-blocking — routes the report to the correct Department Officer
        # based on GPS city detection and issue type → department mapping.
        # Writes kanban_stage=NEW and an audit log entry.
        # ==========================================
        routing_result = {}
        try:
            issue_type_for_routing = (
                ai_result.get("predicted_class", "").lower()
                or issue_category.value.lower()
            )
            routing_result = route_report(
                db=db,
                report=report,
                lat=location_lat,
                lng=location_lng,
                issue_type=issue_type_for_routing,
            )
            db.commit()   # commit routing fields + audit log in one shot
            db.refresh(report)
            if routing_result.get("success"):
                logger.info(
                    f"🚦 Routing: report ID={report.id} → "
                    f"city={routing_result['city']}, "
                    f"dept={routing_result['department']}, "
                    f"officer='{routing_result['officer_name']}'"
                )
            else:
                logger.warning(
                    f"⚠️ Routing incomplete for report ID={report.id}: "
                    f"{routing_result.get('note')}"
                )
        except Exception as routing_exc:
            logger.error(
                f"❌ Routing failed (non-blocking) for report ID={report.id}: "
                f"{routing_exc}",
                exc_info=True,
            )

        # ==========================================
        # STEP 10: RETURN SUCCESS
        # ==========================================
        return {
            "success": True,
            "merged": False,
            "message": ai_result["message"],
            "report": _report_to_dict(report, current_user.id, db),
            "ai_results": {
                "confidence": ai_result["confidence"],
                "severity": ai_result["severity"],
                "final_score": ai_result["final_score"],
                "gps_verification": {
                    "status": ai_result["gps_verification"]["verification_status"],
                    "distance_km": ai_result["gps_verification"].get("distance_km"),
                    "is_spoofed": ai_result["gps_verification"]["is_spoofed"],
                },
            },
            "validation": {
                "quality_score": processing_result["layer0"]["overall_quality"],
                "warnings": processing_result["warnings"],
            },
            "fraud_check": {
                "is_flagged_for_spam": is_flagged_for_spam,
                "hourly_count": fraud_result["hourly_count"],
                "is_duplicate": duplicate_of_id is not None,
                "duplicate_of_id": duplicate_of_id,
                "existing_report": duplicate_report,
            },
            "community_verification": {
                "status": "PENDING"
                if community_verification_created
                else "UNAVAILABLE",
                "request_created": community_verification_created,
            },
            "trust_check": trust_result,
            "final_score_result": score_result,
            "routing": {
                "success":      routing_result.get("success", False),
                "city":         routing_result.get("city"),
                "department":   routing_result.get("department"),
                "officer_id":   routing_result.get("officer_id"),
                "officer_name": routing_result.get("officer_name"),
            },
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
    query = db.query(Report).options(
        joinedload(Report.reporter).joinedload(User.profile)
    )

    if category:
        try:
            cat = IssueCategory(category.upper())
            query = query.filter(Report.category == cat)
        except ValueError:
            pass

    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    if not reports:
        return {"success": True, "count": 0, "reports": []}

    # Increment views in bulk
    report_ids = [r.id for r in reports]
    db.query(Report).filter(Report.id.in_(report_ids)).update(
        {Report.views: Report.views + 1}, synchronize_session=False
    )
    db.commit()

    # Batch-fetch current user's interactions for all reports in one query
    interactions = db.query(ReportInteraction).filter(
        ReportInteraction.report_id.in_(report_ids),
        ReportInteraction.user_id == current_user.id,
    ).all()
    supported_ids = {i.report_id for i in interactions if i.interaction_type == InteractionType.SUPPORT}
    verified_ids  = {i.report_id for i in interactions if i.interaction_type == InteractionType.VERIFY}

    # Batch-fetch comment counts for all reports in one query
    comment_counts = dict(
        db.query(Comment.report_id, func.count(Comment.id))
        .filter(Comment.report_id.in_(report_ids))
        .group_by(Comment.report_id)
        .all()
    )

    result = []
    for report in reports:
        reporter = report.reporter
        reporter_profile = reporter.profile if reporter else None
        full_name = f"{reporter.first_name} {reporter.last_name}" if reporter else "Unknown"
        initials = f"{reporter.first_name[0]}{reporter.last_name[0]}".upper() if reporter else "??"

        result.append({
            "id": report.id,
            "reporter_id": reporter.id if reporter else None,
            "reporter_name": full_name,
            "reporter_initials": initials,
            "reporter_avatar_url": reporter_profile.profile_image_url if reporter_profile else None,
            "timestamp": report.created_at.isoformat(),
            "location": report.location_address,
            "location_city": report.location_city or "",
            "issue_category": report.category.value,
            "title": report.title,
            "description": report.description,
            "image_url": report.image_url or "",
            "views": report.views,
            "support_count": report.support_count,
            "verify_count": report.verify_count,
            "comment_count": comment_counts.get(report.id, 0),
            "status": report.status.value,
            "has_supported": report.id in supported_ids,
            "has_verified": report.id in verified_ids,
        })

    return {"success": True, "count": len(result), "reports": result}


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
        if report.verify_count >= 5 and report.status == ReportStatus.PENDING:
            report.status = ReportStatus.VERIFIED

    db.commit()

    if has_verified:
        ImpactScoreManager(db).award_points(current_user.id, POINTS_VOTE_CAST, "VERIFY_CAST")

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


# ─────────────────────────────────────────────
# COMMENTS
# ─────────────────────────────────────────────

def _comment_to_dict(comment: Comment, current_user_id: int) -> dict:
    user = comment.user
    profile = user.profile if hasattr(user, "profile") else None
    full_name = f"{user.first_name} {user.last_name}"
    initials = f"{user.first_name[0]}{user.last_name[0]}".upper()
    return {
        "id": comment.id,
        "report_id": comment.report_id,
        "user_id": comment.user_id,
        "user_name": full_name,
        "user_initials": initials,
        "user_avatar_url": profile.profile_image_url if profile else None,
        "text": comment.text,
        "created_at": comment.created_at.isoformat(),
        "is_own_comment": comment.user_id == current_user_id,
    }


@router.get("/{report_id}/comments")
def get_comments(
    report_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns paginated comments for a report (oldest first)."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    comments = (
        db.query(Comment)
        .filter(Comment.report_id == report_id)
        .order_by(Comment.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = db.query(func.count(Comment.id)).filter(Comment.report_id == report_id).scalar() or 0

    return {
        "success": True,
        "total": total,
        "comments": [_comment_to_dict(c, current_user.id) for c in comments],
    }


@router.post("/{report_id}/comments")
def create_comment(
    report_id: int,
    text: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a comment to a report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Comment text cannot be empty")
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Comment must be 500 characters or fewer")

    comment = Comment(
        report_id=report_id,
        user_id=current_user.id,
        text=text,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    logger.info(f"💬 Comment #{comment.id} added to report #{report_id} by user {current_user.id}")
    return {
        "success": True,
        "comment": _comment_to_dict(comment, current_user.id),
    }


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete own comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")

    db.delete(comment)
    db.commit()
    logger.info(f"🗑️ Comment #{comment_id} deleted by user {current_user.id}")
    return {"success": True, "message": "Comment deleted"}