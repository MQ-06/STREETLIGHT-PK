"""
Image Storage Manager - Handles temporary storage + Cloudinary upload
"""
import os
import uuid
import logging
import cloudinary
import cloudinary.uploader
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ImageStorage:
    """
    Manages image storage throughout the validation pipeline:
    1. Temporary storage (during AI processing)
    2. Cloudinary upload (after validation passes)
    3. Cleanup (delete temp files)
    """
    
    def __init__(self):
        """Initialize storage manager with temp directory and Cloudinary config"""
        # Temp directory for processing
        self.temp_dir = Path(__file__).parent.parent / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Temp directory: {self.temp_dir}")
        
        # Configure Cloudinary
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        
        if not all([cloud_name, api_key, api_secret]):
            raise ValueError(
                "Cloudinary credentials missing! Please set CLOUDINARY_CLOUD_NAME, "
                "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in your .env file."
            )
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        logger.info(f"☁️ Cloudinary configured: cloud_name={cloud_name}")
    
    def save_temp(self, file: UploadFile) -> str:
        """
        Save uploaded file to temporary storage for AI processing
        
        Args:
            file: Uploaded file from FastAPI
            
        Returns:
            Full path to temporary file
            
        Raises:
            ValueError: If file extension is invalid
            IOError: If file cannot be saved
        """
        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in {'.jpg', '.jpeg', '.png'}:
            raise ValueError(f"Invalid file extension: {file_ext}. Allowed: .jpg, .jpeg, .png")
        
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        temp_path = self.temp_dir / unique_filename
        
        # Save to disk
        logger.info(f"💾 Saving temp file: {unique_filename}")
        try:
            with open(temp_path, "wb") as f:
                content = file.file.read()
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to save temp file: {e}")
            raise IOError(f"Could not save uploaded file: {str(e)}")
        
        # Validate file was saved
        if not temp_path.exists() or temp_path.stat().st_size == 0:
            raise IOError("File saved but appears empty or corrupted")
        
        file_size_mb = temp_path.stat().st_size / (1024 * 1024)
        logger.info(f"✓ Temp file saved: {file_size_mb:.2f} MB")
        return str(temp_path)
    
    def upload_to_cloudinary(self, temp_file_path: str, category: str = "other") -> str:
        """
        Upload validated image to Cloudinary cloud storage.

        Only called AFTER image passes all AI validation checks.

        Args:
            temp_file_path: Path to temporary file
            category:       Cloudinary root folder name — "pothole_img" or "garbage_img"

        Returns:
            Full Cloudinary HTTPS URL (stored in database)

        Raises:
            Exception: If upload fails
        """
        logger.info(f"☁️ Uploading to Cloudinary: {Path(temp_file_path).name} → folder: {category}")

        try:
            # Organise by AI category then date: e.g. pothole_img/2026/03/01/
            now = datetime.now()
            folder = f"{category}/{now.year}/{now.month:02d}/{now.day:02d}"
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                temp_file_path,
                folder=folder,
                resource_type="image",
                unique_filename=True,
                overwrite=False,
            )
            
            # Get the secure HTTPS URL
            cloudinary_url = result["secure_url"]
            
            file_size_kb = result.get("bytes", 0) / 1024
            logger.info(f"✓ Uploaded to Cloudinary: {file_size_kb:.1f} KB")
            logger.info(f"  URL: {cloudinary_url}")
            
            return cloudinary_url
            
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {str(e)}")
            raise Exception(f"Failed to upload image to Cloudinary: {str(e)}")
    
    def cleanup_temp(self, temp_file_path: str):
        """
        Delete temporary file after processing (success or failure)
        
        Args:
            temp_file_path: Path to temporary file
        """
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info(f"🗑️ Cleaned up temp file: {Path(temp_file_path).name}")
        except Exception as e:
            logger.error(f"Failed to cleanup {temp_file_path}: {e}")
    
    def cleanup_old_files(self, max_age_hours: int = 1):
        """
        Clean up temp files older than specified hours
        (Safety measure in case cleanup failed due to crash)
        
        Args:
            max_age_hours: Maximum age in hours before deletion
        """
        import time
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_count = 0
        
        for file_path in self.temp_dir.glob("*"):
            if file_path.is_file():
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.info(f"🗑️ Cleaned up old temp file: {file_path.name}")
                except Exception as e:
                    logger.error(f"Failed to cleanup old file {file_path}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"✓ Cleaned up {cleaned_count} old temp file(s)")
        
        return cleaned_count
