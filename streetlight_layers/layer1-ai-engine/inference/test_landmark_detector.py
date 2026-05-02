"""
Test Script for Landmark Detection and GPS Verification Module

This script demonstrates how to use the landmark detector module
to verify GPS coordinates and detect spoofing.

Usage:
    python test_landmark_detector.py
"""

from pathlib import Path
from landmark_detector import GPSVerifier, ExifExtractor
from landmark_detector.config import (
    SPOOFING_THRESHOLD_KM,
    VERIFIED_THRESHOLD_KM,
    SPOOFING_PENALTY,
    VERIFIED_BONUS
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_exif_extraction():
    """Test EXIF GPS extraction from sample image."""
    print("\n" + "="*60)
    print("TEST 1: EXIF GPS Extraction")
    print("="*60)
    
    # Replace with path to a real image file for testing
    test_image = Path("test_image_with_gps.jpg")
    
    if not test_image.exists():
        print(f"⚠️ Test image not found: {test_image}")
        print("Please provide a test image with GPS data.")
        return None
    
    extractor = ExifExtractor()
    gps_data = extractor.extract_gps(test_image)
    
    if gps_data:
        print(f"✓ GPS Extracted Successfully:")
        print(f"  Latitude: {gps_data['latitude']:.6f}")
        print(f"  Longitude: {gps_data['longitude']:.6f}")
        if 'camera_make' in gps_data:
            print(f"  Camera: {gps_data['camera_make']} {gps_data.get('camera_model', '')}")
        if 'photo_timestamp' in gps_data:
            print(f"  Timestamp: {gps_data['photo_timestamp']}")
        return gps_data
    else:
        print("✗ No GPS data found in image")
        return None


def test_geocoding():
    """Test reverse geocoding with Nominatim API."""
    print("\n" + "="*60)
    print("TEST 2: Reverse Geocoding")
    print("="*60)
    
    from landmark_detector.geocoder import Geocoder
    
    geocoder = Geocoder()
    
    # Test with Lahore coordinates
    test_locations = [
        (31.5204, 74.3587, "Lahore, Punjab"),
        (33.6844, 73.0479, "Islamabad"),
        (24.8607, 67.0011, "Karachi"),
    ]
    
    for lat, lon, expected_city in test_locations:
        print(f"\nTesting: ({lat}, {lon}) - Expected: {expected_city}")
        address = geocoder.get_short_address(lat, lon)
        
        if address:
            print(f"✓ Address: {address}")
        else:
            print("✗ Geocoding failed")


def test_landmark_finding():
    """Test landmark finding with Overpass API."""
    print("\n" + "="*60)
    print("TEST 3: Landmark Finding")
    print("="*60)
    
    from landmark_detector.landmark_finder import LandmarkFinder
    
    finder = LandmarkFinder()
    
    # Test with Lahore Mall Road coordinates
    lat, lon = 31.5582, 74.3100
    print(f"\nSearching landmarks near Mall Road, Lahore ({lat}, {lon})")
    
    landmarks = finder.find_nearby_landmarks(lat, lon, radius_meters=500)
    
    if landmarks:
        print(f"✓ Found {len(landmarks)} landmarks:")
        for i, landmark in enumerate(landmarks, 1):
            print(f"  {i}. {landmark['name']}")
            print(f"     Type: {landmark['type']}, Distance: {landmark['distance_m']}m")
    else:
        print("✗ No landmarks found (API may be unavailable)")


def test_gps_verification():
    """Test complete GPS verification workflow."""
    print("\n" + "="*60)
    print("TEST 4: GPS Verification Workflow")
    print("="*60)
    
    verifier = GPSVerifier()
    
    # Scenario 1: Image without GPS
    print("\n--- Scenario 1: Image without GPS data ---")
    test_image_no_gps = Path("test_image_no_gps.jpg")
    if test_image_no_gps.exists():
        result = verifier.verify_location(test_image_no_gps, 31.5204, 74.3587)
        print(f"Status: {result['verification_status']}")
        print(f"Penalty: {result['penalty_reason']}")
    else:
        print("⚠️ Test image not found, skipping...")
    
    # Scenario 2: GPS match (same coordinates)
    print("\n--- Scenario 2: GPS coordinates match ---")
    print("Simulated: Photo GPS = (31.5204, 74.3587)")
    print("           Submitted = (31.5204, 74.3587)")
    distance = verifier.calculate_distance_km(31.5204, 74.3587, 31.5204, 74.3587)
    print(f"Distance: {distance:.3f} km")
    print(f"Expected: No penalty (0 points)")
    
    # Scenario 3: Minor mismatch (< 5km)
    print("\n--- Scenario 3: Minor GPS mismatch ---")
    print("Simulated: Photo GPS = (31.5204, 74.3587)")
    print("           Submitted = (31.5500, 74.3800)")
    distance = verifier.calculate_distance_km(31.5204, 74.3587, 31.5500, 74.3800)
    print(f"Distance: {distance:.3f} km")
    if distance < SPOOFING_THRESHOLD_KM:
        print(f"Expected: Minor penalty (distance < {SPOOFING_THRESHOLD_KM} km)")
    
    # Scenario 4: GPS Spoofing (> 5km)
    print("\n--- Scenario 4: GPS Spoofing Detected ---")
    print("Simulated: Photo GPS = (31.5204, 74.3587) - Lahore")
    print("           Submitted = (33.6844, 73.0479) - Islamabad")
    distance = verifier.calculate_distance_km(31.5204, 74.3587, 33.6844, 73.0479)
    print(f"Distance: {distance:.3f} km")
    if distance > SPOOFING_THRESHOLD_KM:
        print(f"Expected: ⚠️ SPOOFING DETECTED! Penalty: {SPOOFING_PENALTY} points")
    
    # Scenario 5: Verified location (< 500m with landmarks)
    print("\n--- Scenario 5: Verified Location ---")
    print("Simulated: Photo GPS = (31.5204, 74.3587)")
    print("           Submitted = (31.5210, 74.3590)")
    distance = verifier.calculate_distance_km(31.5204, 74.3587, 31.5210, 74.3590)
    print(f"Distance: {distance:.3f} km")
    if distance < VERIFIED_THRESHOLD_KM:
        print(f"Expected: ✓ Verified! Bonus: +{VERIFIED_BONUS} points")


def test_haversine_formula():
    """Test custom Haversine distance calculation."""
    print("\n" + "="*60)
    print("TEST 5: Haversine Distance Calculation")
    print("="*60)
    
    verifier = GPSVerifier()
    
    # Known distances for verification
    test_cases = [
        ((31.5204, 74.3587), (31.5204, 74.3587), 0.0, "Same location"),
        ((31.5204, 74.3587), (33.6844, 73.0479), 291.0, "Lahore to Islamabad"),
        ((31.5204, 74.3587), (24.8607, 67.0011), 1018.0, "Lahore to Karachi"),
    ]
    
    print("\nTesting Haversine formula accuracy:")
    for (lat1, lon1), (lat2, lon2), expected_km, description in test_cases:
        calculated = verifier.calculate_distance_km(lat1, lon1, lat2, lon2)
        error = abs(calculated - expected_km)
        
        print(f"\n{description}:")
        print(f"  Calculated: {calculated:.2f} km")
        print(f"  Expected: ~{expected_km:.2f} km")
        print(f"  Error: {error:.2f} km")
        
        if error < 10:  # Allow 10km margin for approximation
            print("  ✓ PASS")
        else:
            print("  ⚠️ WARNING: Large error")


def print_configuration():
    """Print current configuration settings."""
    print("\n" + "="*60)
    print("CONFIGURATION SETTINGS")
    print("="*60)
    print(f"Spoofing Threshold: {SPOOFING_THRESHOLD_KM} km")
    print(f"Verified Threshold: {VERIFIED_THRESHOLD_KM} km")
    print(f"Spoofing Penalty: {SPOOFING_PENALTY} points")
    print(f"Verified Bonus: +{VERIFIED_BONUS} points")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🚦 STREETLIGHT GPS VERIFICATION TEST SUITE")
    print("="*60)
    
    print_configuration()
    
    try:
        # Test 1: EXIF extraction (requires test image)
        gps_data = test_exif_extraction()
        
        # Test 2: Geocoding (requires internet)
        test_geocoding()
        
        # Test 3: Landmark finding (requires internet)
        test_landmark_finding()
        
        # Test 4: GPS verification scenarios
        test_gps_verification()
        
        # Test 5: Haversine formula
        test_haversine_formula()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED")
        print("="*60)
        print("\nNote: Some tests require:")
        print("  1. Internet connection (for OpenStreetMap APIs)")
        print("  2. Test images with GPS data")
        print("  3. API rate limits may cause delays")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

