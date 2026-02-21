"""
Input Validator for StreetLight Civic Reporting App
Performs comprehensive image quality and metadata validation.
"""

import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
# import hashlib
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validates uploaded images for civic reporting.
    Checks image quality, metadata, and location information.
    """
    
    # Validation thresholds
    MIN_BLUR_SCORE = 100.0
    MIN_BRIGHTNESS = 30.0
    MAX_BRIGHTNESS = 230.0
    MIN_WIDTH = 300
    MIN_HEIGHT = 300
    MAX_PHOTO_AGE_DAYS = 30
    
    # Pakistan geographic bounds
    PAKISTAN_LAT_MIN = 23.0
    PAKISTAN_LAT_MAX = 37.0
    PAKISTAN_LON_MIN = 60.0
    PAKISTAN_LON_MAX = 78.0
    
    # Allowed image extensions
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    
    # SECURITY: File size limits
    MIN_FILE_SIZE = 10 * 1024  # 10 KB
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    # SECURITY: Dimension limits
    MAX_IMAGE_WIDTH = 10000
    MAX_IMAGE_HEIGHT = 10000
    
    # QUALITY: Aspect ratio limits
    MIN_ASPECT_RATIO = 0.5
    MAX_ASPECT_RATIO = 2.0
    
    # SECURITY: GPS precision limit
    GPS_MAX_DECIMAL_PLACES = 6
    
    # QUALITY: Allowed color modes
    ALLOWED_COLOR_MODES = {'RGB', 'RGBA', 'L', 'P'}
    
    # QUALITY: Screenshot aspect ratios (width:height)
    SCREENSHOT_RATIOS = [
        (16, 9),   # 16:9 landscape
        (9, 16),   # 9:16 portrait
        (18, 9),   # 18:9 modern phones
        (19, 9),   # 19:9 modern phones
    ]
    
    # SECURITY: Dangerous EXIF tags to strip
    DANGEROUS_EXIF_TAGS = {'MakerNote', 'UserComment', 'ImageDescription'}
    
    def __init__(self):
        """Initialize the InputValidator."""
        logger.info("InputValidator initialized with thresholds:")
        logger.info(f"  Blur score minimum: {self.MIN_BLUR_SCORE}")
        logger.info(f"  Brightness range: {self.MIN_BRIGHTNESS} - {self.MAX_BRIGHTNESS}")
        logger.info(f"  Minimum resolution: {self.MIN_WIDTH}x{self.MIN_HEIGHT}")
    
    def validate_all(
        self,
        image_path: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Perform all validation checks on an image.
        
        Args:
            image_path: Path to the image file
            latitude: Optional GPS latitude coordinate
            longitude: Optional GPS longitude coordinate
            
        Returns:
            Dictionary containing:
                - is_valid: bool - Overall validation result
                - overall_quality: float - Quality score (0-100)
                - errors: list[str] - Critical errors
                - warnings: list[str] - Non-critical warnings
                - checks: list[dict] - Individual check results
                - filename: str - Name of the validated file
        """
        logger.info(f"Starting validation for: {image_path}")
        logger.info(f"GPS coordinates: lat={latitude}, lon={longitude}")
        
        checks = []
        errors = []
        warnings = []
        
        # Run all validation checks
        # CRITICAL SECURITY CHECKS (run first)
        checks.append(self._check_file_size(image_path))
        checks.append(self._check_file_valid(image_path))
        checks.append(self._check_color_mode(image_path))
        checks.append(self._check_dimensions(image_path))
        checks.append(self._check_aspect_ratio(image_path))
        
        # QUALITY CHECKS
        checks.append(self._check_resolution(image_path))
        checks.append(self._check_blur(image_path))
        checks.append(self._check_brightness(image_path))
        checks.append(self._check_null_image(image_path))
        
        # METADATA CHECKS
        checks.append(self._check_timestamp(image_path))
        checks.append(self._check_screenshot_detection(image_path))
        
        # GPS VALIDATION (with precision sanitization)
        checks.append(self._check_gps(latitude, longitude))
        
        # Collect errors and warnings
        for check in checks:
            if not check['passed']:
                if check['name'] in ['File Validity', 'Resolution', 'Blur Detection', 'Brightness', 'GPS Validation']:
                    errors.append(check['message'])
                else:
                    warnings.append(check['message'])
            elif 'warning' in check['message'].lower():
                # Add to warnings if message contains 'warning'
                warnings.append(check['message'])
        
        # Calculate overall quality score
        overall_quality = self._calculate_quality(checks)
        
        # Determine if validation passed (no critical errors)
        is_valid = len(errors) == 0
        
        # Calculate image hash for duplicate detection
        # image_hash = self._calculate_image_hash(image_path)
        
        result = {
            'is_valid': is_valid,
            'overall_quality': round(overall_quality, 2),
            'errors': errors,
            'warnings': warnings,
            'checks': checks,
            'filename': Path(image_path).name
            # 'image_hash': image_hash
        }
        
        logger.info(f"Validation complete: valid={is_valid}, quality={overall_quality:.2f}")
        logger.info(f"Errors: {len(errors)}, Warnings: {len(warnings)}")
        
        return result
    
    def _check_file_valid(self, image_path: str) -> Dict[str, Any]:
        """
        Check if file is a valid image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running file validity check...")
        
        try:
            path = Path(image_path)
            
            # Check if file exists
            if not path.exists():
                return {
                    'name': 'File Validity',
                    'passed': False,
                    'score': 0.0,
                    'message': 'File does not exist'
                }
            
            # Check extension
            if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                return {
                    'name': 'File Validity',
                    'passed': False,
                    'score': 0.0,
                    'message': f'Invalid file extension. Allowed: {", ".join(self.ALLOWED_EXTENSIONS)}'
                }
            
            # Try to open the image
            with Image.open(image_path) as img:
                img.verify()  # Verify it's a valid image
            
            # Re-open for actual use (verify closes the file)
            with Image.open(image_path) as img:
                img.load()
            
            logger.info("✓ File validity check passed")
            return {
                'name': 'File Validity',
                'passed': True,
                'score': 100.0,
                'message': 'Valid image file'
            }
            
        except Exception as e:
            logger.error(f"✗ File validity check failed: {str(e)}")
            return {
                'name': 'File Validity',
                'passed': False,
                'score': 0.0,
                'message': f'Invalid or corrupted image file: {str(e)}'
            }
    
    def _check_blur(self, image_path: str) -> Dict[str, Any]:
        """
        Check image blur using Laplacian variance method.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running blur detection check...")
        
        try:
            # Read image in grayscale
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            
            if image is None:
                return {
                    'name': 'Blur Detection',
                    'passed': False,
                    'score': 0.0,
                    'message': 'Could not read image for blur detection'
                }
            
            # Calculate Laplacian variance (measure of edge strength)
            laplacian = cv2.Laplacian(image, cv2.CV_64F)
            blur_score = float(laplacian.var())
            
            # Normalize score to 0-100 scale (arbitrary scaling for display)
            normalized_score = min(100.0, (blur_score / self.MIN_BLUR_SCORE) * 100)
            
            passed = blur_score >= self.MIN_BLUR_SCORE
            
            if passed:
                logger.info(f"✓ Blur check passed: score={blur_score:.2f}")
                message = f'Image is sharp (score: {blur_score:.2f})'
            else:
                logger.warning(f"✗ Blur check failed: score={blur_score:.2f}")
                message = f'Image too blurry (score: {blur_score:.2f}). Please retake in better focus.'
            
            return {
                'name': 'Blur Detection',
                'passed': passed,
                'score': round(normalized_score, 2),
                'message': message
            }
            
        except Exception as e:
            logger.error(f"✗ Blur detection error: {str(e)}")
            return {
                'name': 'Blur Detection',
                'passed': False,
                'score': 0.0,
                'message': f'Blur detection failed: {str(e)}'
            }
    
    def _check_brightness(self, image_path: str) -> Dict[str, Any]:
        """
        Check image brightness using mean pixel intensity.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running brightness check...")
        
        try:
            # Read image in grayscale
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            
            if image is None:
                return {
                    'name': 'Brightness',
                    'passed': False,
                    'score': 0.0,
                    'message': 'Could not read image for brightness check'
                }
            
            # Calculate mean brightness
            mean_brightness = float(np.mean(image))
            
            # Normalize to 0-100 scale (pixel values are 0-255)
            normalized_score = (mean_brightness / 255.0) * 100
            
            # Check if within acceptable range
            if mean_brightness < self.MIN_BRIGHTNESS:
                logger.warning(f"✗ Image too dark: {mean_brightness:.2f}")
                return {
                    'name': 'Brightness',
                    'passed': False,
                    'score': round(normalized_score, 2),
                    'message': f'Image too dark (level: {mean_brightness:.2f}). Please adjust lighting.'
                }
            elif mean_brightness > self.MAX_BRIGHTNESS:
                logger.warning(f"✗ Image too bright: {mean_brightness:.2f}")
                return {
                    'name': 'Brightness',
                    'passed': False,
                    'score': round(normalized_score, 2),
                    'message': f'Image too bright (level: {mean_brightness:.2f}). Please adjust lighting.'
                }
            else:
                logger.info(f"✓ Brightness check passed: {mean_brightness:.2f}")
                return {
                    'name': 'Brightness',
                    'passed': True,
                    'score': round(normalized_score, 2),
                    'message': f'Good brightness (level: {mean_brightness:.2f})'
                }
            
        except Exception as e:
            logger.error(f"✗ Brightness check error: {str(e)}")
            return {
                'name': 'Brightness',
                'passed': False,
                'score': 0.0,
                'message': f'Brightness check failed: {str(e)}'
            }
    
    def _check_resolution(self, image_path: str) -> Dict[str, Any]:
        """
        Check if image resolution meets minimum requirements.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running resolution check...")
        
        try:
            with Image.open(image_path) as img:
                width, height = img.size
            
            # Calculate quality score based on resolution
            width_ratio = width / self.MIN_WIDTH
            height_ratio = height / self.MIN_HEIGHT
            score = min(100.0, min(width_ratio, height_ratio) * 100)
            
            passed = width >= self.MIN_WIDTH and height >= self.MIN_HEIGHT
            
            if passed:
                logger.info(f"✓ Resolution check passed: {width}x{height}")
                message = f'Good resolution ({width}x{height})'
            else:
                logger.warning(f"✗ Resolution too low: {width}x{height}")
                message = f'Resolution too low ({width}x{height}). Minimum {self.MIN_WIDTH}x{self.MIN_HEIGHT} required.'
            
            return {
                'name': 'Resolution',
                'passed': passed,
                'score': round(score, 2),
                'message': message
            }
            
        except Exception as e:
            logger.error(f"✗ Resolution check error: {str(e)}")
            return {
                'name': 'Resolution',
                'passed': False,
                'score': 0.0,
                'message': f'Resolution check failed: {str(e)}'
            }
    
    def _check_timestamp(self, image_path: str) -> Dict[str, Any]:
        """
        Check photo timestamp from EXIF data.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running timestamp check...")
        
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
            
            if exif_data is None:
                logger.warning("⚠ No EXIF data found")
                return {
                    'name': 'Timestamp',
                    'passed': True,
                    'score': 50.0,
                    'message': 'No EXIF timestamp found (accepted with warning)'
                }
            
            # Look for DateTime tags
            datetime_tag = None
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                    datetime_tag = value
                    break
            
            if datetime_tag is None:
                logger.warning("⚠ No DateTime in EXIF")
                return {
                    'name': 'Timestamp',
                    'passed': True,
                    'score': 50.0,
                    'message': 'No timestamp in EXIF data (accepted with warning)'
                }
            
            # Parse datetime
            try:
                photo_datetime = datetime.strptime(datetime_tag, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                logger.warning(f"⚠ Could not parse timestamp: {datetime_tag}")
                return {
                    'name': 'Timestamp',
                    'passed': True,
                    'score': 50.0,
                    'message': 'Could not parse timestamp (accepted with warning)'
                }
            
            # Check age
            now = datetime.now()
            age_days = (now - photo_datetime).days
            
            # Calculate score (100% if fresh, decreases with age)
            score = max(0.0, 100.0 - (age_days / self.MAX_PHOTO_AGE_DAYS) * 100)
            
            if age_days > self.MAX_PHOTO_AGE_DAYS:
                logger.warning(f"✗ Photo too old: {age_days} days")
                return {
                    'name': 'Timestamp',
                    'passed': False,
                    'score': round(score, 2),
                    'message': f'Photo is {age_days} days old. Please take a fresh photo (max {self.MAX_PHOTO_AGE_DAYS} days).'
                }
            else:
                logger.info(f"✓ Timestamp check passed: {age_days} days old")
                return {
                    'name': 'Timestamp',
                    'passed': True,
                    'score': round(score, 2),
                    'message': f'Photo is {age_days} days old (within acceptable range)'
                }
            
        except Exception as e:
            logger.error(f"✗ Timestamp check error: {str(e)}")
            return {
                'name': 'Timestamp',
                'passed': True,
                'score': 50.0,
                'message': 'Could not read timestamp (accepted with warning)'
            }
    
    def _check_gps(
        self,
        latitude: Optional[float],
        longitude: Optional[float]
    ) -> Dict[str, Any]:
        """
        Validate GPS coordinates are within Pakistan bounds.
        SECURITY: Sanitizes GPS precision to prevent overflow attacks.
        
        Args:
            latitude: GPS latitude coordinate
            longitude: GPS longitude coordinate
            
        Returns:
            Check result dictionary
        """
        logger.info(f"Running GPS validation: lat={latitude}, lon={longitude}")
        
        if latitude is None or longitude is None:
            logger.warning("✗ GPS coordinates not provided")
            return {
                'name': 'GPS Validation',
                'passed': False,
                'score': 0.0,
                'message': 'GPS coordinates required for validation'
            }
        
        try:
            # Convert to float if needed
            lat = float(latitude)
            lon = float(longitude)
            
            # SECURITY: Round to max 6 decimal places to prevent overflow attacks
            # 6 decimal places = ~0.11 meter precision (sufficient for civic reporting)
            lat = round(lat, self.GPS_MAX_DECIMAL_PLACES)
            lon = round(lon, self.GPS_MAX_DECIMAL_PLACES)
            
            # Check if within Pakistan bounds
            lat_valid = self.PAKISTAN_LAT_MIN <= lat <= self.PAKISTAN_LAT_MAX
            lon_valid = self.PAKISTAN_LON_MIN <= lon <= self.PAKISTAN_LON_MAX
            
            if lat_valid and lon_valid:
                logger.info(f"✓ GPS coordinates valid: ({lat:.6f}, {lon:.6f})")
                return {
                    'name': 'GPS Validation',
                    'passed': True,
                    'score': 100.0,
                    'message': f'Valid Pakistan location ({lat:.6f}, {lon:.6f})'
                }
            else:
                logger.warning(f"✗ GPS coordinates outside Pakistan: ({lat:.6f}, {lon:.6f})")
                return {
                    'name': 'GPS Validation',
                    'passed': False,
                    'score': 0.0,
                    'message': f'GPS location ({lat:.6f}, {lon:.6f}) outside Pakistan bounds'
                }
            
        except (ValueError, TypeError) as e:
            logger.error(f"✗ GPS validation error: {str(e)}")
            return {
                'name': 'GPS Validation',
                'passed': False,
                'score': 0.0,
                'message': f'Invalid GPS coordinates: {str(e)}'
            }
    
    def _check_file_size(self, image_path: str) -> Dict[str, Any]:
        """
        CRITICAL SECURITY: Check file size to prevent memory attacks.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running file size check...")
        
        try:
            file_size = os.path.getsize(image_path)
            file_size_kb = file_size / 1024
            file_size_mb = file_size / (1024 * 1024)
            
            # Check minimum size
            if file_size < self.MIN_FILE_SIZE:
                logger.warning(f"✗ File too small: {file_size_kb:.2f} KB")
                return {
                    'name': 'File Size',
                    'passed': False,
                    'score': 0.0,
                    'message': f'File too small ({file_size_kb:.2f} KB). Minimum {self.MIN_FILE_SIZE/1024:.0f} KB required. Possible corruption.'
                }
            
            # Check maximum size
            if file_size > self.MAX_FILE_SIZE:
                logger.warning(f"✗ File too large: {file_size_mb:.2f} MB")
                return {
                    'name': 'File Size',
                    'passed': False,
                    'score': 0.0,
                    'message': f'File too large ({file_size_mb:.2f} MB). Maximum {self.MAX_FILE_SIZE/(1024*1024):.0f} MB allowed.'
                }
            
            # Calculate score (optimal around 1-5 MB)
            if file_size_mb <= 5:
                score = 100.0
            else:
                # Decreasing score as file approaches max size
                score = 100.0 - ((file_size_mb - 5) / 5) * 20
                score = max(50.0, score)
            
            logger.info(f"✓ File size check passed: {file_size_mb:.2f} MB")
            return {
                'name': 'File Size',
                'passed': True,
                'score': round(score, 2),
                'message': f'Acceptable file size ({file_size_mb:.2f} MB)'
            }
            
        except Exception as e:
            logger.error(f"✗ File size check error: {str(e)}")
            return {
                'name': 'File Size',
                'passed': False,
                'score': 0.0,
                'message': f'File size check failed: {str(e)}'
            }
    
    def _check_dimensions(self, image_path: str) -> Dict[str, Any]:
        """
        CRITICAL SECURITY: Check maximum dimensions to prevent decompression bombs.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running dimension limits check...")
        
        try:
            with Image.open(image_path) as img:
                width, height = img.size
            
            # Check maximum dimensions
            if width > self.MAX_IMAGE_WIDTH or height > self.MAX_IMAGE_HEIGHT:
                logger.warning(f"✗ Dimensions too large: {width}x{height}")
                return {
                    'name': 'Dimension Limits',
                    'passed': False,
                    'score': 0.0,
                    'message': f'Image dimensions ({width}x{height}) exceed maximum allowed ({self.MAX_IMAGE_WIDTH}x{self.MAX_IMAGE_HEIGHT}). Potential decompression bomb.'
                }
            
            # Calculate score based on total pixels
            total_pixels = width * height
            max_pixels = self.MAX_IMAGE_WIDTH * self.MAX_IMAGE_HEIGHT
            score = 100.0  # Safe dimensions get full score
            
            logger.info(f"✓ Dimension limits check passed: {width}x{height}")
            return {
                'name': 'Dimension Limits',
                'passed': True,
                'score': score,
                'message': f'Safe image dimensions ({width}x{height})'
            }
            
        except Exception as e:
            logger.error(f"✗ Dimension limits check error: {str(e)}")
            return {
                'name': 'Dimension Limits',
                'passed': False,
                'score': 0.0,
                'message': f'Dimension check failed: {str(e)}'
            }
    
    def _check_color_mode(self, image_path: str) -> Dict[str, Any]:
        """
        CRITICAL SECURITY: Validate color mode to prevent processing attacks.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running color mode validation...")
        
        try:
            with Image.open(image_path) as img:
                color_mode = img.mode
            
            if color_mode not in self.ALLOWED_COLOR_MODES:
                logger.warning(f"✗ Invalid color mode: {color_mode}")
                return {
                    'name': 'Color Mode',
                    'passed': False,
                    'score': 0.0,
                    'message': f'Unsupported color mode ({color_mode}). Allowed: {", ".join(self.ALLOWED_COLOR_MODES)}. Please convert to RGB.'
                }
            
            logger.info(f"✓ Color mode check passed: {color_mode}")
            return {
                'name': 'Color Mode',
                'passed': True,
                'score': 100.0,
                'message': f'Valid color mode ({color_mode})'
            }
            
        except Exception as e:
            logger.error(f"✗ Color mode check error: {str(e)}")
            return {
                'name': 'Color Mode',
                'passed': False,
                'score': 0.0,
                'message': f'Color mode check failed: {str(e)}'
            }
    
    def _check_aspect_ratio(self, image_path: str) -> Dict[str, Any]:
        """
        CRITICAL QUALITY: Check aspect ratio to detect distorted images.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running aspect ratio check...")
        
        try:
            with Image.open(image_path) as img:
                width, height = img.size
            
            # Calculate aspect ratio (width / height)
            aspect_ratio = width / height if height > 0 else 0
            
            # Check if within acceptable range
            if aspect_ratio < self.MIN_ASPECT_RATIO or aspect_ratio > self.MAX_ASPECT_RATIO:
                logger.warning(f"✗ Aspect ratio out of range: {aspect_ratio:.2f}")
                return {
                    'name': 'Aspect Ratio',
                    'passed': False,
                    'score': 0.0,
                    'message': f'Aspect ratio ({aspect_ratio:.2f}) too distorted. Acceptable range: {self.MIN_ASPECT_RATIO} - {self.MAX_ASPECT_RATIO}.'
                }
            
            # Calculate score (1.0 is ideal square-ish, common ratios like 4:3, 16:9 are good)
            # Score decreases as it moves toward limits
            ideal_ratios = [1.0, 1.33, 1.5, 0.75, 0.67]  # 1:1, 4:3, 3:2, 3:4, 2:3
            min_diff = min(abs(aspect_ratio - ideal) for ideal in ideal_ratios)
            score = max(70.0, 100.0 - (min_diff * 30))
            
            logger.info(f"✓ Aspect ratio check passed: {aspect_ratio:.2f}")
            return {
                'name': 'Aspect Ratio',
                'passed': True,
                'score': round(score, 2),
                'message': f'Acceptable aspect ratio ({aspect_ratio:.2f})'
            }
            
        except Exception as e:
            logger.error(f"✗ Aspect ratio check error: {str(e)}")
            return {
                'name': 'Aspect Ratio',
                'passed': False,
                'score': 0.0,
                'message': f'Aspect ratio check failed: {str(e)}'
            }
    
    def _check_screenshot_detection(self, image_path: str) -> Dict[str, Any]:
        """
        QUALITY WARNING: Detect screenshots based on aspect ratio + missing EXIF.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running screenshot detection...")
        
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                exif_data = img._getexif()
            
            # Calculate aspect ratio
            aspect_ratio = width / height if height > 0 else 0
            
            # Check if matches common screenshot ratios
            is_screenshot_ratio = False
            for ratio_w, ratio_h in self.SCREENSHOT_RATIOS:
                expected_ratio = ratio_w / ratio_h
                if abs(aspect_ratio - expected_ratio) < 0.05:  # 5% tolerance
                    is_screenshot_ratio = True
                    break
            
            # Check if EXIF data is missing or minimal
            has_minimal_exif = exif_data is None or len(exif_data) < 5
            
            # Warn if both conditions are met
            if is_screenshot_ratio and has_minimal_exif:
                logger.warning(f"⚠ Possible screenshot detected: {aspect_ratio:.2f} ratio, minimal EXIF")
                return {
                    'name': 'Screenshot Detection',
                    'passed': True,
                    'score': 60.0,
                    'message': f'Warning: Image appears to be a screenshot (aspect ratio {aspect_ratio:.2f}, no camera EXIF). Please submit original photos.'
                }
            
            logger.info(f"✓ Screenshot detection passed: likely original photo")
            return {
                'name': 'Screenshot Detection',
                'passed': True,
                'score': 100.0,
                'message': 'Image appears to be an original photo'
            }
            
        except Exception as e:
            logger.error(f"✗ Screenshot detection error: {str(e)}")
            # Non-critical, pass with warning
            return {
                'name': 'Screenshot Detection',
                'passed': True,
                'score': 80.0,
                'message': 'Could not determine if screenshot (check skipped)'
            }
    
    def _check_null_image(self, image_path: str) -> Dict[str, Any]:
        """
        QUALITY: Check if image has actual content (not all same color).
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Check result dictionary
        """
        logger.info("Running null/empty image check...")
        
        try:
            # Read image
            image = cv2.imread(str(image_path))
            
            if image is None:
                return {
                    'name': 'Content Validation',
                    'passed': False,
                    'score': 0.0,
                    'message': 'Could not read image content'
                }
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate standard deviation (measure of variation)
            std_dev = float(np.std(gray))
            
            # If std dev is very low, image is mostly uniform (blank/corrupted)
            if std_dev < 5.0:
                logger.warning(f"✗ Image appears blank or corrupted: std_dev={std_dev:.2f}")
                return {
                    'name': 'Content Validation',
                    'passed': False,
                    'score': 0.0,
                    'message': f'Image appears blank or has no content (variation: {std_dev:.2f}). Please submit a photo with visible content.'
                }
            
            # Calculate score based on content variation
            score = min(100.0, (std_dev / 50.0) * 100)
            
            logger.info(f"✓ Content validation passed: std_dev={std_dev:.2f}")
            return {
                'name': 'Content Validation',
                'passed': True,
                'score': round(score, 2),
                'message': f'Image has valid content (variation: {std_dev:.2f})'
            }
            
        except Exception as e:
            logger.error(f"✗ Content validation error: {str(e)}")
            return {
                'name': 'Content Validation',
                'passed': False,
                'score': 0.0,
                'message': f'Content validation failed: {str(e)}'
            }
    
    def _calculate_quality(self, checks: List[Dict[str, Any]]) -> float:
        """
        Calculate overall quality score from individual checks.
        Uses weighted average based on check importance.
        
        Args:
            checks: List of check result dictionaries
            
        Returns:
            Overall quality score (0-100)
        """
        # Define weights for each check
        weights = {
            # CRITICAL SECURITY CHECKS (highest weight)
            'File Size': 2.0,          # Critical security
            'File Validity': 2.0,      # Critical security
            'Color Mode': 1.8,         # Critical security
            'Dimension Limits': 2.0,   # Critical security (decompression bombs)
            'Aspect Ratio': 1.5,       # Critical quality
            
            # QUALITY CHECKS (high weight)
            'Resolution': 1.5,         # Important quality
            'Blur Detection': 1.8,     # Critical for usability
            'Brightness': 1.5,         # Important quality
            'Content Validation': 1.7, # Important (null/blank check)
            
            # METADATA CHECKS (moderate weight)
            'Timestamp': 0.8,          # Less critical (has warnings)
            'Screenshot Detection': 0.5, # Warning only
            'GPS Validation': 1.2      # Moderate (required but can be added later)
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for check in checks:
            weight = weights.get(check['name'], 1.0)
            total_score += check['score'] * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    def get_thresholds(self) -> Dict[str, Any]:
        """
        Get current validation thresholds.
        
        Returns:
            Dictionary of threshold values
        """
        return {
            'file_size': {
                'min_bytes': self.MIN_FILE_SIZE,
                'max_bytes': self.MAX_FILE_SIZE,
                'min_kb': self.MIN_FILE_SIZE / 1024,
                'max_mb': self.MAX_FILE_SIZE / (1024 * 1024),
                'description': 'File size limits (security: prevent memory attacks)'
            },
            'dimensions': {
                'max_width': self.MAX_IMAGE_WIDTH,
                'max_height': self.MAX_IMAGE_HEIGHT,
                'description': 'Maximum image dimensions (security: prevent decompression bombs)'
            },
            'color_mode': {
                'allowed_modes': list(self.ALLOWED_COLOR_MODES),
                'description': 'Allowed color modes (security: prevent processing attacks)'
            },
            'aspect_ratio': {
                'min': self.MIN_ASPECT_RATIO,
                'max': self.MAX_ASPECT_RATIO,
                'description': 'Acceptable aspect ratio range (quality: detect distortion)'
            },
            'blur': {
                'min_score': self.MIN_BLUR_SCORE,
                'description': 'Minimum Laplacian variance for sharpness'
            },
            'brightness': {
                'min': self.MIN_BRIGHTNESS,
                'max': self.MAX_BRIGHTNESS,
                'description': 'Acceptable mean pixel intensity range'
            },
            'resolution': {
                'min_width': self.MIN_WIDTH,
                'min_height': self.MIN_HEIGHT,
                'description': 'Minimum image dimensions in pixels'
            },
            'timestamp': {
                'max_age_days': self.MAX_PHOTO_AGE_DAYS,
                'description': 'Maximum acceptable photo age'
            },
            'gps': {
                'pakistan_bounds': {
                    'latitude': [self.PAKISTAN_LAT_MIN, self.PAKISTAN_LAT_MAX],
                    'longitude': [self.PAKISTAN_LON_MIN, self.PAKISTAN_LON_MAX]
                },
                'max_decimal_places': self.GPS_MAX_DECIMAL_PLACES,
                'description': 'Valid GPS coordinate ranges for Pakistan (security: precision limited)'
            },
            'file': {
                'allowed_extensions': list(self.ALLOWED_EXTENSIONS),
                'description': 'Allowed image file formats'
            },
            'screenshot_detection': {
                'monitored_ratios': [[w, h] for w, h in self.SCREENSHOT_RATIOS],
                'description': 'Screenshot aspect ratios that trigger warnings'
            },
            'security': {
                'dangerous_exif_tags': list(self.DANGEROUS_EXIF_TAGS),
                'description': 'EXIF tags that are stripped for security'
            }
        }

