"""
GPS Verifier Module
Main verification logic for detecting GPS spoofing and calculating penalties.
"""

import logging
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path
from typing import Dict, Optional, Tuple
from .config import (
    SPOOFING_THRESHOLD_KM,
    VERIFIED_THRESHOLD_KM,
    SPOOFING_PENALTY,
    VERIFIED_BONUS,
    NO_GPS_PENALTY,
    ERROR_NO_GPS,
    ERROR_INVALID_GPS,
    ERROR_API_FAILURE,
    ERROR_INVALID_SUBMITTED_GPS,
    SUCCESS_VERIFIED,
    SUCCESS_MATCH,
    WARNING_MISMATCH,
    WARNING_SPOOFING
)
from .exif_extractor import ExifExtractor
from .geocoder import Geocoder
from .landmark_finder import LandmarkFinder

logger = logging.getLogger(__name__)


class GPSVerifier:
    """
    Main GPS verification class.
    Coordinates EXIF extraction, geocoding, landmark finding, and score calculation.
    """
    
    def __init__(self):
        self.exif_extractor = ExifExtractor()
        self.geocoder = Geocoder()
        self.landmark_finder = LandmarkFinder()
    
    def verify_location(
        self,
        image_path: Path,
        submitted_lat: Optional[float] = None,
        submitted_lon: Optional[float] = None
    ) -> Dict:
        """
        Main verification method - compares photo GPS with submitted GPS.
        
        Args:
            image_path: Path to uploaded image
            submitted_lat: User-submitted latitude (optional)
            submitted_lon: User-submitted longitude (optional)
            
        Returns:
            Dictionary containing verification results:
            {
                'has_photo_gps': bool,
                'photo_gps': tuple or None,
                'submitted_gps': tuple or None,
                'photo_address': str,
                'submitted_address': str,
                'distance_km': float,
                'nearby_landmarks': list,
                'is_spoofed': bool,
                'score_adjustment': int,
                'penalty_reason': str,
                'verification_status': str
            }
        """
        result = {
            'has_photo_gps': False,
            'photo_gps': None,
            'submitted_gps': None,
            'photo_address': None,
            'submitted_address': None,
            'distance_km': None,
            'nearby_landmarks': [],
            'is_spoofed': False,
            'score_adjustment': NO_GPS_PENALTY,
            'penalty_reason': '',
            'verification_status': 'unknown'
        }
        
        # Step 1: Extract GPS from photo
        logger.info("Step 1: Extracting GPS from photo EXIF...")
        photo_gps_data = self.exif_extractor.extract_gps(image_path)
        
        if not photo_gps_data:
            result['verification_status'] = 'no_gps_in_photo'
            result['penalty_reason'] = ERROR_NO_GPS
            logger.info("⚠ No GPS data in photo - verification skipped")
            return result
        
        # Extract coordinates
        photo_lat = photo_gps_data['latitude']
        photo_lon = photo_gps_data['longitude']
        result['photo_gps'] = (photo_lat, photo_lon)
        result['has_photo_gps'] = True
        
        logger.info(f"✓ Photo GPS: ({photo_lat:.6f}, {photo_lon:.6f})")
        
        # Step 2: Validate submitted GPS (if provided)
        if submitted_lat is not None and submitted_lon is not None:
            if not self._is_valid_coordinate(submitted_lat, submitted_lon):
                result['verification_status'] = 'invalid_submitted_gps'
                result['penalty_reason'] = ERROR_INVALID_SUBMITTED_GPS
                logger.warning("⚠ Invalid submitted GPS coordinates")
                return result
            
            result['submitted_gps'] = (submitted_lat, submitted_lon)
            logger.info(f"Submitted GPS: ({submitted_lat:.6f}, {submitted_lon:.6f})")
        else:
            # No submitted GPS - just geocode photo location
            logger.info("No submitted GPS - verifying photo location only")
            result['submitted_gps'] = result['photo_gps']
            submitted_lat = photo_lat
            submitted_lon = photo_lon
        
        # Step 3: Calculate distance
        logger.info("Step 2: Calculating distance...")
        distance_km = self.calculate_distance_km(
            photo_lat, photo_lon,
            submitted_lat, submitted_lon
        )
        result['distance_km'] = round(distance_km, 3)
        logger.info(f"Distance: {distance_km:.3f} km")
        
        # Step 4: Geocode both locations
        logger.info("Step 3: Geocoding locations...")
        try:
            photo_address = self.geocoder.get_short_address(photo_lat, photo_lon)
            if photo_address:
                result['photo_address'] = photo_address
                logger.info(f"Photo location: {photo_address}")
            
            if distance_km > 0.1:  # Only geocode submitted if different
                submitted_address = self.geocoder.get_short_address(submitted_lat, submitted_lon)
                if submitted_address:
                    result['submitted_address'] = submitted_address
                    logger.info(f"Submitted location: {submitted_address}")
            else:
                result['submitted_address'] = result['photo_address']
                
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
            result['penalty_reason'] = ERROR_API_FAILURE
        
        # Step 5: Find nearby landmarks (use photo GPS)
        logger.info("Step 4: Finding nearby landmarks...")
        try:
            landmarks = self.landmark_finder.find_nearby_landmarks(photo_lat, photo_lon)
            result['nearby_landmarks'] = landmarks
            logger.info(f"Found {len(landmarks)} landmarks")
        except Exception as e:
            logger.error(f"Landmark search error: {str(e)}")
        
        # Step 6: Determine spoofing and calculate penalty
        logger.info("Step 5: Calculating verification score...")
        score_adjustment, is_spoofed, status, reason = self._calculate_score_adjustment(
            distance_km,
            len(result['nearby_landmarks'])
        )
        
        result['score_adjustment'] = score_adjustment
        result['is_spoofed'] = is_spoofed
        result['verification_status'] = status
        result['penalty_reason'] = reason
        
        logger.info(f"✓ Verification complete: {status} (adjustment: {score_adjustment:+d})")
        
        return result
    
    def _calculate_score_adjustment(
        self,
        distance_km: float,
        num_landmarks: int
    ) -> Tuple[int, bool, str, str]:
        """
        Calculate score adjustment based on distance and landmarks.
        
        Args:
            distance_km: Distance between photo and submitted GPS
            num_landmarks: Number of nearby landmarks found
            
        Returns:
            Tuple of (score_adjustment, is_spoofed, status, reason)
        """
        # Case 1: GPS Spoofing detected (> 5km)
        if distance_km > SPOOFING_THRESHOLD_KM:
            return (
                SPOOFING_PENALTY,
                True,
                'spoofing_detected',
                f"{WARNING_SPOOFING} (distance: {distance_km:.2f} km)"
            )
        
        # Case 2: Verified location (< 500m with landmarks)
        if distance_km < VERIFIED_THRESHOLD_KM and num_landmarks >= 2:
            return (
                VERIFIED_BONUS,
                False,
                'verified',
                f"{SUCCESS_VERIFIED} ({num_landmarks} landmarks within 500m)"
            )
        
        # Case 3: Good match (< 500m but few landmarks)
        if distance_km < VERIFIED_THRESHOLD_KM:
            return (
                0,
                False,
                'good_match',
                f"{SUCCESS_MATCH} (distance: {distance_km:.2f} km)"
            )
        
        # Case 4: Acceptable mismatch (500m - 5km)
        if distance_km < SPOOFING_THRESHOLD_KM:
            penalty = int(-10 * (distance_km / SPOOFING_THRESHOLD_KM))  # Gradual penalty
            return (
                penalty,
                False,
                'minor_mismatch',
                f"{WARNING_MISMATCH} (distance: {distance_km:.2f} km)"
            )
        
        # Default case
        return (0, False, 'unknown', '')
    
    @staticmethod
    def calculate_distance_km(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula.
        
        Args:
            lat1: Latitude of first point (decimal degrees)
            lon1: Longitude of first point (decimal degrees)
            lat2: Latitude of second point (decimal degrees)
            lon2: Longitude of second point (decimal degrees)
            
        Returns:
            Distance in kilometers
        """
        # Earth's radius in kilometers
        R = 6371.0
        
        # Convert degrees to radians
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        
        return distance
    
    @staticmethod
    def _is_valid_coordinate(latitude: float, longitude: float) -> bool:
        """
        Validate GPS coordinates.
        
        Args:
            latitude: Latitude value
            longitude: Longitude value
            
        Returns:
            True if valid, False otherwise
        """
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lon <= 180):
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False

