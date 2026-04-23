# 🚦 StreetLight Layer 0 - Input Validation

<!-- Validates images before entering the processing pipeline, ensuring only high-quality, secure data is accepted. -->

---

## ✨ Validation Checks

### 🔒 Security (Critical)
1. **File Size** - 10 KB to 10 MB (prevents memory attacks)
2. **Dimensions** - Max 10000×10000 (prevents decompression bombs)
3. **Color Mode** - RGB/RGBA/L/P only (prevents processing attacks)
4. **Aspect Ratio** - 0.5 to 2.0 (detects distortion)

### 🎨 Quality (Important)
5. **File Validity** - Checks for corruption
6. **Resolution** - Minimum 300×300 pixels
7. **Blur Detection** - Laplacian variance (min 100)
8. **Brightness** - Range 30-230 (proper lighting)
9. **Content** - Detects blank/null images

### 📍 Metadata
10. **Timestamp** - Max 30 days old (EXIF)
11. **GPS Location** - Pakistan bounds (23-37°N, 60-78°E)
12. **Screenshot Detection** - Warns if screenshot detected

<!-- **Plus:** SHA-256 hash generation for duplicate detection -->

---

## 📁 Structure

```
layer0-input-validation/
├── backend/
│   ├── validators/input_validator.py    # Core validation
│   ├── main.py                          # FastAPI server
│   └── requirements.txt
├── frontend/index.html                  # Web testing interface
├── test_images/                         # Generated test images
└── utils/create_test_images.py          # Test data generator
```

---

## 🚀 Quick Start

### 1. Setup
```bash
# Navigate to directory
cd D:\FYP\STREETLIGHT\streetlight_layers\layer0-input-validation

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
cd backend
pip install -r requirements.txt

# Generate test images
cd ../utils
python create_test_images.py
```

---

### 2. Run Backend
```bash
cd backend
uvicorn main:app --reload
```
**Server:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### 3. Open Frontend
```bash
cd frontend
python -m http.server 8080
```
**Web UI:** http://localhost:8080

### 4. Test
- Upload test images from `test_images/` folder
- Try GPS coordinates: Lahore (31.5204, 74.3587) or New York (40.7128, -74.0060)
- View validation results in real-time

---


### Main Endpoint: POST /api/validate

**Request:**
```bash
curl -X POST http://localhost:8000/api/validate \
  -F "image=@image.jpg" \
  -F "latitude=31.5204" \
  -F "longitude=74.3587"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "overall_quality": 92.5,
    "errors": [],
    "warnings": ["No EXIF timestamp found"],
    "checks": [ /* 12 validation results */ ],
    "filename": "image.jpg",
    "image_hash": "sha256_hash_here"
  }
}
```

**Other Endpoints:**
- `GET /health` - Health check
- `GET /api/thresholds` - View all validation thresholds
- `GET /docs` - Interactive API documentation

---

### Option 1: Direct Import
```python
from validators.input_validator import InputValidator

validator = InputValidator()

# In your report submission endpoint
@app.post("/api/reports/submit")
async def submit_report(image, latitude, longitude):
    # Validate first
    result = validator.validate_all(image_path, latitude, longitude)
    
    if not result['is_valid']:
        return {"error": result['errors']}
    
    # Continue processing...
    save_report({
        'image_hash': result['image_hash'],  # For duplicate detection
        'quality_score': result['overall_quality']
    })
```

### Option 2: Microservice
Call Layer 0 as a standalone service:
```python
import httpx

response = await httpx.post(
    'http://layer0-service:8000/api/validate',
    files={'image': image_file},
    data={'latitude': lat, 'longitude': lon}
)
```

**See INTEGRATION_GUIDE.md for detailed integration strategies.**

---

