"""
FastAPI Backend for StreetLight AI Engine
Provides REST API endpoints for image classification.

Usage:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Optional
import sys
import uuid
import os
import logging
from datetime import datetime

# Add inference directory to path
INFERENCE_DIR = Path(__file__).parent.parent / "inference"
sys.path.insert(0, str(INFERENCE_DIR))

from ai_engine import AIEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="StreetLight AI Engine API",
    description="Image classification API for civic reporting (pothole/garbage detection)",
    version="1.0.0"
)

# Configure CORS (allow all origins for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
MODELS_DIR = Path(__file__).parent.parent / "training" / "models"
MODEL_PATH = MODELS_DIR / "best_model.pth"
UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

# Global AI Engine instance
ai_engine = None


@app.on_event("startup")
async def startup_event():
    """Initialize AI engine on startup."""
    global ai_engine
    
    logger.info("="*60)
    logger.info("StreetLight AI Engine API Starting")
    logger.info("="*60)
    
    # Check if model exists
    if not MODEL_PATH.exists():
        logger.error(f"Model not found: {MODEL_PATH}")
        logger.error("\nPlease train model first:")
        logger.error("  cd ../training")
        logger.error("  python train.py")
        logger.error("\nAPI will start but predictions will fail until model is available.")
        return
    
    try:
        # Load AI engine
        logger.info(f"Loading model from: {MODEL_PATH}")
        ai_engine = AIEngine(MODEL_PATH, confidence_threshold=0.70)

        # Get model info
        model_info = ai_engine.get_model_info()
        logger.info(f"✓ Model loaded successfully")
        logger.info(f"  Classes: {model_info['classes']}")
        logger.info(f"  Model: {model_info['model_name']}")
        logger.info(f"  Device: {model_info['device']}")
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        logger.error("API will start but predictions will fail.")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down API...")
    
    # Clean up temporary uploads
    try:
        for file in UPLOADS_DIR.glob("*"):
            if file.is_file():
                os.remove(file)
                logger.info(f"Cleaned up: {file}")
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")


@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "service": "StreetLight AI Engine",
        "version": "1.0.0",
        "description": "Image classification API for civic reporting",
        "model_status": "loaded" if ai_engine is not None else "not_loaded",
        "endpoints": {
            "POST /api/predict": "Upload image for classification",
            "GET /health": "Health check",
            "GET /api/model-info": "Model metadata"
        },
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    model_loaded = ai_engine is not None
    
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/model-info")
async def get_model_info():
    """
    Get model metadata and information.
    
    Returns:
        Model information including classes, accuracy, and configuration
    """
    if ai_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs."
        )
    
    try:
        model_info = ai_engine.get_model_info()
        return {
            "success": True,
            "model_info": model_info
        }
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predict")
async def predict_image(
    image: UploadFile = File(...),
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
):
    """
    Predict class of uploaded image with GPS verification.
    
    Args:
        image: Image file (jpg, jpeg, png)
        latitude: User-submitted latitude (optional)
        longitude: User-submitted longitude (optional)
        
    Returns:
        Prediction results including class, confidence, severity, GPS verification, and analysis
    """
    if ai_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train model first and restart server."
        )
    
    temp_file_path = None
    
    try:
        logger.info(f"Received prediction request for: {image.filename}")
        
        # Validate file type
        file_extension = Path(image.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file_extension}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        temp_file_path = UPLOADS_DIR / unique_filename
        
        # Save uploaded file
        logger.info(f"Saving to: {temp_file_path}")
        with open(temp_file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Validate file size
        file_size = os.path.getsize(temp_file_path)
        logger.info(f"File size: {file_size} bytes")
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        if file_size > 10 * 1024 * 1024:  # 10 MB limit
            raise HTTPException(status_code=400, detail="File too large (max 10 MB)")
        
        # Predict with GPS verification
        logger.info("Running prediction with GPS verification...")
        if latitude is not None and longitude is not None:
            logger.info(f"Submitted GPS: ({latitude}, {longitude})")
        
        result = ai_engine.predict(
            temp_file_path,
            submitted_lat=latitude,
            submitted_lon=longitude
        )
        
        # Add request metadata
        result['request_info'] = {
            'original_filename': image.filename,
            'file_size_bytes': file_size,
            'content_type': image.content_type,
            'submitted_gps': (latitude, longitude) if latitude and longitude else None
        }
        
        logger.info(f"Prediction complete: {result['predicted_class']} ({result['confidence']:.2f}%)")
        logger.info(f"Final score: {result['final_score']:.2f} (AI: {result['ai_score']:.2f}, "
                   f"GPS adjustment: {result['gps_verification']['score_adjustment']:+d})")
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
        
    finally:
        # Clean up temp file
        if temp_file_path and temp_file_path.exists():
            try:
                os.remove(temp_file_path)
                logger.info(f"Cleaned up: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to cleanup temp file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server with uvicorn...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
