#main.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import signup, login, forget_password, reset_password
from routers.flutter import mobile_auth
from middleware.cors import setup_cors
import logging

from model.users import User
from model.user_profile import UserProfile
from model.report import Report, ReportInteraction 
from utils.image_storage import ImageStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="StreetLight Civic Reporting API",
    description="AI-powered civic reporting system with automated validation",
    version="1.0.0"
)

setup_cors(app)

# Serve uploaded report images at /uploads
uploads_dir = Path(__file__).parent / "uploads"
if uploads_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(forget_password.router)
app.include_router(reset_password.router)
app.include_router(mobile_auth.router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize AI layers and cleanup on startup
    """
    logger.info("=" * 70)
    logger.info("🚦 STREETLIGHT BACKEND STARTING")
    logger.info("=" * 70)
    
    try:
        # AI layers are initialized when mobile_auth module loads
        logger.info("✓ AI Agent initialized (loaded with mobile_auth router)")
        
        # Initialize image storage and cleanup old temp files
        logger.info("Initializing image storage...")
        storage = ImageStorage()
        logger.info("✓ Image storage initialized")
        
        # Clean up old temp files from previous crashes
        logger.info("Cleaning up old temp files...")
        cleaned = storage.cleanup_old_files(max_age_hours=1)
        if cleaned > 0:
            logger.info(f"✓ Cleaned up {cleaned} old temp file(s)")
        else:
            logger.info("✓ No old temp files to clean")
        
        logger.info("=" * 70)
        logger.info("✅ STREETLIGHT BACKEND READY")
        logger.info("📍 AI Agent is operational and ready to process reports")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ STARTUP ERROR: {str(e)}")
        logger.error("Report creation will fail until this is fixed!")
        logger.error("=" * 70)


@app.get("/")
def root():
    return {
        "message": "StreetLight Backend Running",
        "version": "1.0.0",
        "ai_agent": "operational",
        "features": [
            "Automated image validation",
            "AI-powered classification",
            "GPS verification",
            "Severity estimation"
        ]
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "streetlight-api",
        "ai_agent": "operational"
    }