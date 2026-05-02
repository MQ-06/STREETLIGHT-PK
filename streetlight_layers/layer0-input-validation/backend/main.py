"""
FastAPI Backend for Layer 0 Input Validation
StreetLight Civic Reporting App
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from validators.input_validator import InputValidator
from pathlib import Path
from typing import Optional
import uuid
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="StreetLight Layer 0 - Input Validation API",
    description="Image quality and metadata validation service for civic reporting",
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

# Initialize validator
validator = InputValidator()

# Create temp directory for uploaded files
TEMP_DIR = Path(__file__).parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

logger.info("FastAPI server initialized")
logger.info(f"Temp directory: {TEMP_DIR}")


@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "service": "StreetLight Layer 0 - Input Validation",
        "version": "1.0.0",
        "description": "Validates images for civic reporting submissions",
        "endpoints": {
            "POST /api/validate": "Validate an uploaded image",
            "GET /health": "Health check",
            "GET /api/thresholds": "Get validation thresholds"
        },
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "input-validation",
        "validator": "operational"
    }


@app.get("/api/thresholds")
async def get_thresholds():
    """
    Get current validation thresholds.
    
    Returns:
        Dictionary of threshold values used for validation
    """
    try:
        thresholds = validator.get_thresholds()
        return {
            "success": True,
            "thresholds": thresholds
        }
    except Exception as e:
        logger.error(f"Error getting thresholds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate")
async def validate_image(
    image: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None)
):
    """
    Validate an uploaded image for civic reporting.
    
    Args:
        image: Image file to validate (jpg, jpeg, png)
        latitude: Optional GPS latitude coordinate
        longitude: Optional GPS longitude coordinate
        
    Returns:
        Validation results including quality score and specific checks
    """
    temp_file_path = None
    
    try:
        logger.info(f"Received validation request for: {image.filename}")
        logger.info(f"GPS coordinates: lat={latitude}, lon={longitude}")
        
        # Validate file type
        file_extension = Path(image.filename).suffix.lower()
        if file_extension not in {'.jpg', '.jpeg', '.png'}:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file_extension}. Allowed: .jpg, .jpeg, .png"
            )
        
        # Generate unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        temp_file_path = TEMP_DIR / unique_filename
        
        # Save uploaded file to temp location
        logger.info(f"Saving to temp file: {temp_file_path}")
        with open(temp_file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Validate file size (basic check)
        file_size = os.path.getsize(temp_file_path)
        logger.info(f"File size: {file_size} bytes")
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Perform validation
        logger.info("Running validation checks...")
        result = validator.validate_all(
            image_path=str(temp_file_path),
            latitude=latitude,
            longitude=longitude
        )
        
        # Add request metadata
        result['request_info'] = {
            'original_filename': image.filename,
            'file_size_bytes': file_size,
            'content_type': image.content_type
        }
        
        logger.info(f"Validation complete: valid={result['is_valid']}")
        
        # Return dict directly - FastAPI will handle JSON serialization
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )
        
    finally:
        # Clean up temp file
        if temp_file_path and temp_file_path.exists():
            try:
                os.remove(temp_file_path)
                logger.info(f"Cleaned up temp file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to cleanup temp file: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on server startup.
    """
    logger.info("=" * 60)
    logger.info("StreetLight Layer 0 - Input Validation API Starting")
    logger.info("=" * 60)
    logger.info("Validator initialized with thresholds:")
    thresholds = validator.get_thresholds()
    for key, value in thresholds.items():
        logger.info(f"  {key}: {value.get('description', '')}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on server shutdown.
    """
    logger.info("Shutting down server...")
    
    # Clean up any remaining temp files
    try:
        for temp_file in TEMP_DIR.glob("*"):
            if temp_file.is_file():
                os.remove(temp_file)
                logger.info(f"Cleaned up: {temp_file}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server directly with uvicorn...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

