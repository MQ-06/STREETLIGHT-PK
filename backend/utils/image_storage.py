"""
Image Storage Manager - Handles temporary and permanent local storage
"""
import os
import uuid
import logging
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from datetime import datetime

logger = logging.getLogger(__name__)


class ImageStorage:
    """
    Manages image storage throughout the validation pipeline:
    1. Temporary storage (during AI processing)
    2. Permanent local storage (after validation passes)
    3. Cleanup (delete temp files)
    """
    
    def __init__(self):
        """Initialize storage manager with temp and permanent directories"""
        # Temp directory for processing
        self.temp_dir = Path(__file__).parent.parent / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Temp directory: {self.temp_dir}")
        
        # Permanent storage directory (local)
        self.uploads_dir = Path(__file__).parent.parent / "uploads" / "reports"
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Permanent storage directory: {self.uploads_dir}")
    
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
    
    def save_permanent(self, temp_file_path: str) -> str:
        """
        Move validated image from temp to permanent local storage
        
        Only called AFTER image passes all AI validation checks.
        
        Args:
            temp_file_path: Path to temporary file
            
        Returns:
            Relative path to permanent file (for storing in database)
            
        Raises:
            Exception: If save fails
        """
        logger.info(f"💾 Moving to permanent storage: {Path(temp_file_path).name}")
        
        try:
            # Generate unique filename with date organization
            temp_path = Path(temp_file_path)
            file_ext = temp_path.suffix
            
            # Organize by date: uploads/reports/2026/02/21/uuid.jpg
            now = datetime.now()
            date_dir = self.uploads_dir / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
            date_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            permanent_path = date_dir / unique_filename
            
            # Move file from temp to permanent
            shutil.move(str(temp_path), str(permanent_path))
            
            file_size_kb = permanent_path.stat().st_size / 1024
            logger.info(f"✓ Saved to permanent storage: {file_size_kb:.1f} KB")
            
            # Return relative path for database storage
            relative_path = permanent_path.relative_to(self.uploads_dir.parent)
            logger.info(f"Relative path: {relative_path}")
            
            return str(relative_path).replace("\\", "/")  # Use forward slashes for consistency
            
        except Exception as e:
            logger.error(f"Permanent save failed: {str(e)}")
            raise Exception(f"Failed to save image to permanent storage: {str(e)}")
    
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

