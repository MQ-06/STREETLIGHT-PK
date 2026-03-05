"""
Landmark Detection and GPS Verification Module

This module provides GPS spoofing detection for civic reports by:
1. Extracting GPS coordinates from photo EXIF data
2. Comparing photo GPS with user-submitted GPS
3. Geocoding locations to human-readable addresses
4. Finding nearby landmarks for verification
5. Calculating penalties for GPS mismatches

Usage:
    from landmark_detector import GPSVerifier
    
    verifier = GPSVerifier()
    result = verifier.verify_location(
        image_path=Path("photo.jpg"),
        submitted_lat=31.5204,
        submitted_lon=74.3587
    )
    
    print(f"Distance: {result['distance_km']} km")
    print(f"Score adjustment: {result['score_adjustment']}")
    print(f"Is spoofed: {result['is_spoofed']}")
"""

from .verifier import GPSVerifier
from .exif_extractor import ExifExtractor
from .geocoder import Geocoder
from .landmark_finder import LandmarkFinder
from .config import (
    SPOOFING_THRESHOLD_KM,
    VERIFIED_THRESHOLD_KM,
    SPOOFING_PENALTY,
    VERIFIED_BONUS
)

__version__ = "1.0.0"
__all__ = [
    'GPSVerifier',
    'ExifExtractor',
    'Geocoder',
    'LandmarkFinder',
    'SPOOFING_THRESHOLD_KM',
    'VERIFIED_THRESHOLD_KM',
    'SPOOFING_PENALTY',
    'VERIFIED_BONUS'
]

