# 🚦 StreetLight Layer 1: AI Engine

**Engine A - AI Image Analysis & GPS Verification**

Complete AI-powered system for civic report validation, combining computer vision, GPS verification, and landmark detection to score report authenticity.

---

## 🎯 What It Does

### **Core Features**

1. **Image Classification**
   - Identifies potholes vs garbage vs other
   - Uses ResNet18 trained on Pakistani street images
   - Confidence scoring (0-100)

2. **Severity Assessment** (Hybrid Approach)
   - **Size-based**: Measures actual area coverage using contour detection
   - **Feature-based**: Analyzes dark pixels, edges, texture
   - Combines both methods for accuracy
   - Output: `small`, `medium`, `large`

3. **GPS Verification & Landmark Detection**
   - Extracts GPS from photo EXIF metadata
   - Compares with user-submitted GPS
   - Detects spoofing (>5km = -50 points penalty)
   - Finds nearby landmarks using OpenStreetMap
   - Geocodes locations to readable addresses

4. **Final Scoring**
   ```
   final_score = ai_confidence + gps_adjustment
   Range: 0-100
   ```

---

## 📊 Output Example

```json
{
  "predicted_class": "pothole",
  "confidence": 92.5,
  "ai_score": 92.5,
  "severity": "large",
  "gps_verification": {
    "has_photo_gps": true,
    "photo_gps": [31.5204, 74.3587],
    "submitted_gps": [31.5210, 74.3590],
    "photo_address": "Mall Road, Lahore, Punjab",
    "distance_km": 0.067,
    "nearby_landmarks": [
      {"name": "Lahore Museum", "distance_m": 150.5}
    ],
    "is_spoofed": false,
    "score_adjustment": 10,
    "verification_status": "verified"
  },
  "final_score": 100,
  "message": "Clear pothole detected with 92.5% confidence. ✓ Location verified."
}
```

---

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
cd streetlight_layers/layer1-ai-engine/inference
pip install -r requirements.txt
```

**Requirements:**
- PyTorch (for AI model)
- OpenCV (for image processing)
- Pillow (for EXIF extraction)
- requests (for OpenStreetMap APIs)

### **2. Start the API Server**

```bash
cd ../backend
uvicorn main:app --reload --port 8000
```

Server runs at: `http://localhost:8000`

### **3. Test the API**

#### **Option A: Interactive Docs**
Open: `http://localhost:8000/docs`

#### **Option B: Command Line**
```bash
# With GPS verification
curl -X POST http://localhost:8000/api/predict \
  -F "image=@photo.jpg" \
  -F "latitude=31.5204" \
  -F "longitude=74.3587"

# Without GPS (uses photo GPS only)
curl -X POST http://localhost:8000/api/predict \
  -F "image=@photo.jpg"
```

#### **Option C: Python**
```python
from pathlib import Path
from ai_engine import AIEngine

engine = AIEngine(Path("../training/models/best_model.pth"))
result = engine.predict(
    "photo.jpg",
    submitted_lat=31.5204,
    submitted_lon=74.3587
)

print(f"Class: {result['predicted_class']}")
print(f"Severity: {result['severity']}")
print(f"Final Score: {result['final_score']}")
```


### **Scoring Logic**

| Component | Weight | Range | Source |
|-----------|--------|-------|--------|
| **AI Classification** | Base | 0-100 | ResNet18 confidence |
| **GPS Verification** | Adjustment | -50 to +10 | Distance-based |
| **Final Score** | Combined | 0-100 | Clamped result |

**GPS Adjustments:**
- 🚨 **-50 points**: Distance >5km (spoofing)
- ⚠️ **-10 to 0**: Distance 500m-5km (minor mismatch)
- ✅ **+10 points**: Distance <500m with landmarks (verified)
- ℹ️ **0 points**: No GPS in photo (no penalty)

---

## 🌍 APIs Used (Free, No Keys Required)

### **1. Nominatim (Reverse Geocoding)**
- Converts GPS → Address
- Provider: OpenStreetMap
- Rate Limit: 1 request/second (auto-handled)

### **2. Overpass API (Landmarks)**
- Finds nearby points of interest
- Provider: OpenStreetMap
- Returns: Shops, buildings, roads, amenities

---

