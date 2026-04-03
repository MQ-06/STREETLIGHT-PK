#main.py
from fastapi import FastAPI
from routers import signup, login, forget_password, reset_password
from routers.flutter import mobile_auth
from routers.flutter import verification
from routers.flutter import users
from routers.flutter import trust
from routers.flutter import score
from routers.flutter import notifications
from routers.admin import auth as admin_auth
from routers.admin import dashboard as admin_dashboard
from routers.admin import reports as admin_reports
from middleware.cors import setup_cors
import logging

from model.users import User
from model.user_profile import UserProfile
from model.report import Report, ReportInteraction
from model.verification import VerificationRequest, VerificationVote
from model.routing_table import RoutingTable
from model.report_logs import ReportLog
from model.field_worker_tokens import FieldWorkerToken
from utils.image_storage import ImageStorage
from script.migrate_add_report_contribution_and_fields import migrate as migrate_report_fields
from script.migrate_notifications import run_migration as migrate_notifications
from script.migrate_admin_schema import run_migration as migrate_admin_schema
from utils.push import init_firebase

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

# Images are now served from Cloudinary — no local static mount needed

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(forget_password.router)
app.include_router(reset_password.router)
app.include_router(mobile_auth.router)
app.include_router(verification.router)
app.include_router(users.router)
app.include_router(trust.router)
app.include_router(score.router)
app.include_router(notifications.router)
app.include_router(admin_auth.router)
app.include_router(admin_dashboard.router)
app.include_router(admin_reports.router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize AI layers and cleanup on startup
    """
    logger.info("=" * 70)
    logger.info("🚦 STREETLIGHT BACKEND STARTING")
    logger.info("=" * 70)
    
    try:
        # Ensure DB schema is compatible with current models
        logger.info("Ensuring database schema is up to date...")
        migrate_report_fields()
        migrate_notifications()
        migrate_admin_schema()
        logger.info("✓ Database schema ensured")

        # AI layers are initialized when mobile_auth module loads
        logger.info("✓ AI Agent initialized (loaded with mobile_auth router)")
        
        # Initialize image storage and cleanup old temp files
        logger.info("Initializing image storage...")
        storage = ImageStorage()
        logger.info("✓ Image storage initialized")

        # Best-effort init for push notifications (Phase 2)
        init_firebase()
        
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