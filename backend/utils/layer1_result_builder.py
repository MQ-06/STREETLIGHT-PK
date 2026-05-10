"""
Build full Layer 1 result dict on the API host when classification runs on a remote service.
Uses GPS + hashing + messages without importing PyTorch.
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ai_layers.layer1_ai_engine.landmark_detector.verifier import GPSVerifier

logger = logging.getLogger(__name__)


def _calculate_hash(image_path: Path) -> str:
    try:
        sha256_hash = hashlib.sha256()
        with open(image_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Hash calculation error: {e}")
        return "hash_unavailable"


def _generate_message(
    predicted_class: str,
    confidence: float,
    is_valid: bool,
    gps_verification: Dict,
) -> str:
    confidence_pct = confidence * 100
    if gps_verification.get("is_spoofed", False):
        return (
            f"⚠️ GPS SPOOFING DETECTED: The photo's location differs from your "
            f"submitted location by {gps_verification.get('distance_km', 0):.2f} km. "
            f"Please ensure you're submitting accurate coordinates. "
            f"Penalty applied: {gps_verification.get('score_adjustment', 0)} points."
        )
    if not is_valid:
        if predicted_class == "other":
            return (
                "Image not recognized as a civic issue (pothole or garbage). "
                "If this is street garbage or a road pothole, please retake "
                "the photo in clear daylight with the issue filling most of "
                "the frame."
            )
        return (
            f"Low confidence detection ({confidence_pct:.1f}%). "
            f"The {predicted_class} is not clearly visible. "
            "Please retake the photo from a closer angle with better lighting."
        )
    if confidence_pct >= 90:
        quality = "Clear"
    elif confidence_pct >= 70:
        quality = "Good"
    else:
        quality = "Acceptable"
    base_message = f"{quality} {predicted_class} detected with {confidence_pct:.1f}% confidence."
    if gps_verification.get("verification_status") == "verified":
        base_message += " ✓ Location verified with nearby landmarks."
    elif gps_verification.get("verification_status") == "good_match":
        base_message += " ✓ Location matches submitted coordinates."
    elif gps_verification.get("verification_status") == "minor_mismatch":
        base_message += (
            f" ⚠️ Minor location mismatch "
            f"({gps_verification.get('distance_km', 0):.2f} km)."
        )
    return base_message


def build_layer1_from_remote_json(
    image_path: str,
    latitude: Optional[float],
    longitude: Optional[float],
    remote: Dict[str, Any],
    confidence_threshold: float = 0.68,
) -> Dict[str, Any]:
    """
    Merge remote classifier JSON with local GPS verification and scoring.
    Remote must provide: predicted_class, confidence (%), confidence_raw (0-1),
    all_probabilities, is_valid_issue (optional).
    """
    path = Path(image_path)
    predicted_class = str(remote["predicted_class"])
    confidence_pct = float(remote["confidence"])
    confidence_raw = float(remote.get("confidence_raw", confidence_pct / 100.0))
    all_probs = dict(remote.get("all_probabilities") or {})
    is_valid_issue = bool(
        remote["is_valid_issue"]
        if "is_valid_issue" in remote
        else (
            predicted_class != "other" and confidence_raw >= confidence_threshold
        )
    )

    gps_verifier = GPSVerifier()
    gps_verification = gps_verifier.verify_location(
        image_path=path,
        submitted_lat=latitude,
        submitted_lon=longitude,
    )

    image_hash = _calculate_hash(path)
    # Severity heuristics need OpenCV-heavy code; use medium (matches many cases).
    severity: Optional[str] = "medium" if is_valid_issue else None

    ai_score = round(confidence_raw * 100, 2)
    score_adjustment = gps_verification.get("score_adjustment", 0)
    severity_bonus = {"large": 5, "medium": 0, "small": -5}.get(severity or "medium", 0)
    final_score = max(0, min(100, ai_score + score_adjustment + severity_bonus))

    message = _generate_message(
        predicted_class, confidence_raw, is_valid_issue, gps_verification
    )

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence_pct, 2),
        "ai_score": ai_score,
        "severity": severity,
        "all_probabilities": {k: round(float(v), 2) for k, v in all_probs.items()},
        "image_hash": image_hash,
        "is_valid_issue": is_valid_issue,
        "ood_rejected": False,
        "gps_verification": {
            "has_photo_gps": gps_verification.get("has_photo_gps", False),
            "photo_gps": gps_verification.get("photo_gps"),
            "submitted_gps": gps_verification.get("submitted_gps"),
            "photo_address": gps_verification.get("photo_address"),
            "submitted_address": gps_verification.get("submitted_address"),
            "distance_km": gps_verification.get("distance_km"),
            "nearby_landmarks": gps_verification.get("nearby_landmarks", []),
            "is_spoofed": gps_verification.get("is_spoofed", False),
            "score_adjustment": score_adjustment,
            "verification_status": gps_verification.get("verification_status", "unknown"),
            "penalty_reason": gps_verification.get("penalty_reason", ""),
        },
        "final_score": round(final_score, 2),
        "message": message,
        "remote_classifier": True,
    }
