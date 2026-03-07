# backend/routers/flutter/verification.py
import math
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from model.users import User
from model.user_profile import UserProfile
from model.report import Report
from model.verification import VerificationRequest, VerificationStatus, VoteChoice
from utils.auth_utils import get_current_user, get_db
from ai_layers.layer3_community_verification.community_engine import CommunityVerificationEngine

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────
FEED_RADIUS_KM: float = 2.0   # Show pending requests within 2 km of the user

router = APIRouter(prefix="/verification", tags=["Verification"])


# ── Module-level helpers ────────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two GPS coordinates (Haversine)."""
    R = 6_371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi    = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def _update_user_location(db: Session, user_id: int, lat: float, lng: float) -> None:
    """Persist the user's latest GPS position to UserProfile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        profile.last_known_lat = lat
        profile.last_known_lng = lng
        db.commit()


# ── Request schema ──────────────────────────────────────────────────────────

class VoteRequest(BaseModel):
    vote: str               # "YES" or "NO"
    lat: Optional[float] = None
    lng: Optional[float] = None


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/pending")
def get_pending_verifications(
    lat: float,
    lng: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return PENDING verification requests within 2 km of the user's GPS position.

    Also runs a lazy expiry check so stale requests are cleaned up without
    needing a background scheduler.

    Query params:
        lat  — User's current latitude
        lng  — User's current longitude
    """
    try:
        logger.info(
            f"📍 Layer 3 — get_pending: user={current_user.id} "
            f"GPS=({lat:.6f}, {lng:.6f})"
        )

        # Lazy expiry check — keeps the list fresh on every call
        engine = CommunityVerificationEngine(db)
        expired = engine.finalize_expired_requests()
        if expired:
            logger.info(f"   ⏳ Lazily expired {expired} request(s)")

        # Persist this GPS fix so the user appears in future nearby searches
        _update_user_location(db, current_user.id, lat, lng)

        # Load all PENDING requests (with their linked reports via relationship)
        pending = (
            db.query(VerificationRequest)
            .filter(VerificationRequest.status == VerificationStatus.PENDING)
            .all()
        )

        # Distance filter + serialisation
        result_items = []
        for req in pending:
            report: Optional[Report] = req.report
            if report is None or report.location_lat is None or report.location_lng is None:
                continue

            dist_km = _haversine_km(lat, lng, report.location_lat, report.location_lng)
            if dist_km > FEED_RADIUS_KM:
                continue

            result_items.append({
                "request_id": req.id,
                "report_id":  report.id,
                "title":      report.title,
                "image_url":  report.image_url or "",
                "category":   report.category.value,
                "distance_m": round(dist_km * 1_000.0, 1),
                "created_at": req.created_at.isoformat(),
                "total_votes": req.total_votes,
                "min_votes":   req.min_votes,
            })

        result_items.sort(key=lambda x: x["distance_m"])   # nearest first

        logger.info(
            f"   ✅ {len(result_items)} pending request(s) within {FEED_RADIUS_KM} km"
        )

        return {
            "success": True,
            "count":    len(result_items),
            "requests": result_items,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ get_pending_verifications error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/{request_id}/vote")
def submit_vote(
    request_id: int,
    body: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit a YES or NO community vote on a VerificationRequest.

    Body:
        vote  — "YES" or "NO"
        lat   — Voter's current latitude  (optional)
        lng   — Voter's current longitude (optional)
    """
    try:
        logger.info(
            f"🗳️  Layer 3 — submit_vote: user={current_user.id} "
            f"request={request_id} vote={body.vote!r}"
        )

        # Validate vote string → VoteChoice enum
        try:
            vote_choice = VoteChoice(body.vote.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid vote '{body.vote}'. Must be 'YES' or 'NO'.",
            )

        engine = CommunityVerificationEngine(db)

        try:
            vote_result = engine.submit_vote(
                request_id=request_id,
                user_id=current_user.id,
                vote=vote_choice,
                user_lat=body.lat,
                user_lng=body.lng,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Update user GPS if provided
        if body.lat is not None and body.lng is not None:
            _update_user_location(db, current_user.id, body.lat, body.lng)

        logger.info(
            f"   ✅ Vote accepted: request={request_id} | "
            f"finalised={vote_result['score_finalised']}"
        )

        return {
            "success": True,
            "message": "Vote recorded",
            **vote_result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ submit_vote error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/{report_id}/status")
def get_verification_status(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the community verification status for a specific report.

    Returns 404 if no VerificationRequest has been created for this report.
    """
    try:
        logger.info(
            f"🔍 Layer 3 — get_status: report={report_id} user={current_user.id}"
        )

        engine = CommunityVerificationEngine(db)
        verification = engine.get_verification_status(report_id)

        if verification is None:
            raise HTTPException(
                status_code=404,
                detail=f"No verification request found for report ID={report_id}",
            )

        return {
            "success":      True,
            "verification": verification,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ get_verification_status error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
