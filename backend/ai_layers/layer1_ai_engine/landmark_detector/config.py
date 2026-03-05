"""
Configuration for Landmark Detection and GPS Verification Module
Contains API endpoints, thresholds, and scoring rules.
"""

# API Endpoints
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/reverse"
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"

# User Agent (required by OpenStreetMap policies)
USER_AGENT = "StreetLight-Pakistan-Civic-Reporting/1.0"

# API Timeout Settings (seconds)
GEOCODING_TIMEOUT = 10
LANDMARK_TIMEOUT = 15

# Rate Limiting (to respect API fair use)
NOMINATIM_DELAY = 1.0  # seconds between requests (required by Nominatim)

# Distance Thresholds (kilometers)
SPOOFING_THRESHOLD_KM = 5.0      # Distance > 5km = GPS spoofing
VERIFIED_THRESHOLD_KM = 0.5      # Distance < 500m = verified location
LANDMARK_SEARCH_RADIUS_M = 500   # Search radius for nearby landmarks

# Scoring Adjustments
SPOOFING_PENALTY = -50           # Penalty for GPS mismatch > 5km
VERIFIED_BONUS = 10              # Bonus for verified location < 500m with landmarks
NO_GPS_PENALTY = 0               # No penalty if photo lacks GPS data

# Landmark Categories (Overpass API query types)
LANDMARK_CATEGORIES = [
    "amenity",      # shops, restaurants, schools, etc.
    "building",     # named buildings
    "shop",         # retail shops
    "highway",      # named roads, streets
    "leisure",      # parks, playgrounds
    "natural",      # natural features
    "historic",     # monuments, memorials
]

# Geocoding Result Settings
MIN_ADDRESS_CONFIDENCE = 0.3  # Minimum confidence for address match
MAX_LANDMARKS_RETURN = 5       # Maximum number of landmarks to return

# Error Messages
ERROR_NO_GPS = "No GPS data found in photo"
ERROR_INVALID_GPS = "Invalid GPS coordinates in photo"
ERROR_API_FAILURE = "Location verification service unavailable"
ERROR_INVALID_SUBMITTED_GPS = "Invalid submitted GPS coordinates"

# Success Messages
SUCCESS_VERIFIED = "Location verified with nearby landmarks"
SUCCESS_MATCH = "Photo GPS matches submitted location"
WARNING_MISMATCH = "GPS coordinates do not match photo location"
WARNING_SPOOFING = "Possible GPS spoofing detected"

