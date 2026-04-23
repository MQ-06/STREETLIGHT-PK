# 📍 Landmark Detection & GPS Verification Module

## Overview

This module detects GPS spoofing in civic reports by comparing photo EXIF GPS data with user-submitted coordinates. It uses free OpenStreetMap APIs to verify locations and applies penalties for GPS mismatches.

## 🎯 Features

- **EXIF GPS Extraction** - Reads GPS coordinates embedded in photos by smartphone cameras
- **Reverse Geocoding** - Converts GPS coordinates to readable addresses using Nominatim API
- **Landmark Finding** - Locates nearby points of interest using Overpass API
- **Spoofing Detection** - Flags reports where photo GPS differs from submitted GPS by >5km
- **Automatic Scoring** - Applies -50 point penalty for spoofing, +10 bonus for verified locations

## 📁 Module Structure

```
landmark_detector/
├── __init__.py           # Package exports
├── config.py             # Configuration constants and thresholds
├── exif_extractor.py     # Extract GPS from photo EXIF metadata
├── geocoder.py           # Reverse geocoding (GPS → Address)
├── landmark_finder.py    # Find nearby landmarks (Overpass API)
├── verifier.py           # Main verification logic with Haversine formula
└── README.md             # This file
```

## 🚀 Quick Start

### Basic Usage

```python
from pathlib import Path
from landmark_detector import GPSVerifier

# Initialize verifier
verifier = GPSVerifier()

# Verify location
result = verifier.verify_location(
    image_path=Path("pothole_photo.jpg"),
    submitted_lat=31.5204,  # User's submitted GPS
    submitted_lon=74.3587
)

# Check results
print(f"Distance: {result['distance_km']} km")
print(f"Is spoofed: {result['is_spoofed']}")
print(f"Score adjustment: {result['score_adjustment']}")
print(f"Photo location: {result['photo_address']}")
```

### Integration with AI Engine

```python
from ai_engine import AIEngine

# Initialize AI engine (GPS verifier is automatically initialized)
engine = AIEngine(model_path="best_model.pth")

# Predict with GPS verification
result = engine.predict(
    image_path="pothole.jpg",
    submitted_lat=31.5204,
    submitted_lon=74.3587
)

# Access results
print(f"AI Score: {result['ai_score']}")
print(f"GPS Adjustment: {result['gps_verification']['score_adjustment']}")
print(f"Final Score: {result['final_score']}")
```

## 📊 Verification Logic

### Distance Thresholds

| Distance | Status | Score Adjustment | Description |
|----------|--------|------------------|-------------|
| > 5 km | 🚨 Spoofing | **-50 points** | GPS coordinates don't match |
| < 500m with landmarks | ✅ Verified | **+10 points** | Location confirmed with nearby POIs |
| < 500m | ✓ Good Match | **0 points** | Coordinates match |
| 500m - 5km | ⚠️ Minor Mismatch | **-10 to 0 points** | Gradual penalty based on distance |

### Scoring Formula

```python
final_score = AI_confidence + GPS_adjustment
final_score = max(0, min(100, final_score))  # Clamp to 0-100
```

## 🔧 Configuration

Edit `config.py` to customize thresholds:

```python
# Distance Thresholds (kilometers)
SPOOFING_THRESHOLD_KM = 5.0      # Distance > 5km = spoofing
VERIFIED_THRESHOLD_KM = 0.5      # Distance < 500m = verified

# Scoring Adjustments
SPOOFING_PENALTY = -50           # Penalty for GPS mismatch
VERIFIED_BONUS = 10              # Bonus for verified location

# API Settings
NOMINATIM_DELAY = 1.0            # Seconds between requests
LANDMARK_SEARCH_RADIUS_M = 500   # Search radius for landmarks
```

## 🌍 APIs Used

### 1. Nominatim (Reverse Geocoding)
- **Provider**: OpenStreetMap
- **Endpoint**: `https://nominatim.openstreetmap.org/reverse`
- **Rate Limit**: 1 request/second
- **Cost**: Free
- **Coverage**: Worldwide (including all of Pakistan)

### 2. Overpass API (Landmarks)
- **Provider**: OpenStreetMap
- **Endpoint**: `https://overpass-api.de/api/interpreter`
- **Rate Limit**: Reasonable use
- **Cost**: Free
- **Returns**: Nearby amenities, shops, roads, buildings

## 📐 Haversine Distance Calculation

The module uses a custom Haversine formula implementation (no external dependencies):

```python
def calculate_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in km
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c
```

## 📝 Response Format

```python
{
    'has_photo_gps': True,
    'photo_gps': (31.5204, 74.3587),
    'submitted_gps': (31.5210, 74.3590),
    'photo_address': 'Mall Road, Lahore, Punjab',
    'submitted_address': 'Mall Road, Lahore, Punjab',
    'distance_km': 0.067,
    'nearby_landmarks': [
        {
            'name': 'Lahore Museum',
            'type': 'museum',
            'category': 'amenity',
            'distance_m': 150.5,
            'lat': 31.5205,
            'lon': 74.3588
        }
    ],
    'is_spoofed': False,
    'score_adjustment': 10,
    'verification_status': 'verified',
    'penalty_reason': 'Location verified with nearby landmarks'
}
```

## 🧪 Testing

Run the test suite:

```bash
cd inference
python test_landmark_detector.py
```

Tests include:
- ✅ EXIF GPS extraction
- ✅ Reverse geocoding
- ✅ Landmark finding
- ✅ Spoofing detection scenarios
- ✅ Haversine formula accuracy

## ⚠️ Edge Cases Handled

1. **No GPS in Photo** - Returns `no_gps_in_photo` status, no penalty
2. **Invalid Coordinates** - Returns error status
3. **API Failures** - Gracefully degrades, logs errors
4. **Rate Limiting** - Automatic 1-second delay between Nominatim requests
5. **No Landmarks Found** - Still calculates distance, no bonus applied

## 🔒 Privacy & Security

- **No Data Storage** - GPS data is processed in real-time, not stored
- **User Agent Required** - Respects OpenStreetMap usage policies
- **Rate Limiting** - Prevents API abuse
- **Error Handling** - Fails gracefully without exposing sensitive info

## 📦 Dependencies

```
Pillow>=10.0.0      # EXIF extraction
requests>=2.31.0    # API calls
```

**Note**: Uses built-in `math` library for Haversine formula (no geopy needed)

## 🚦 Usage in StreetLight API

### API Endpoint

```bash
POST /api/predict
Content-Type: multipart/form-data

Parameters:
  - image: file (required)
  - latitude: float (optional)
  - longitude: float (optional)
```

### Example with cURL

```bash
curl -X POST http://localhost:8000/api/predict \
  -F "image=@pothole.jpg" \
  -F "latitude=31.5204" \
  -F "longitude=74.3587"
```

### Response

```json
{
  "success": true,
  "data": {
    "predicted_class": "pothole",
    "confidence": 92.5,
    "ai_score": 92.5,
    "severity": "large",
    "gps_verification": {
      "has_photo_gps": true,
      "distance_km": 0.067,
      "is_spoofed": false,
      "score_adjustment": 10,
      "verification_status": "verified"
    },
    "final_score": 100,
    "message": "Clear pothole detected with 92.5% confidence. ✓ Location verified with nearby landmarks."
  }
}
```

## 🛠️ Troubleshooting

### Issue: "No GPS data found in photo"
- **Cause**: Photo doesn't have EXIF GPS data
- **Solution**: Ensure location services are enabled when taking photos

### Issue: "Geocoding request timed out"
- **Cause**: Nominatim API is slow or unavailable
- **Solution**: Increase `GEOCODING_TIMEOUT` in config.py

### Issue: "No landmarks found"
- **Cause**: Remote area with few POIs in OpenStreetMap
- **Solution**: Normal behavior, verification still works based on distance

### Issue: Rate limit errors
- **Cause**: Too many requests to Nominatim
- **Solution**: Module automatically handles this with 1-second delays

## 📚 References

- [OpenStreetMap Nominatim API](https://nominatim.org/release-docs/latest/api/Reverse/)
- [Overpass API Documentation](https://wiki.openstreetmap.org/wiki/Overpass_API)
- [EXIF GPS Format](https://exiftool.org/TagNames/GPS.html)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)

## 📄 License

Part of the StreetLight civic reporting system.

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Maintainer**: StreetLight Team

