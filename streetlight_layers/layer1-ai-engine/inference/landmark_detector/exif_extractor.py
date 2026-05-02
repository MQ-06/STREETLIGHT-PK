"""
EXIF Extractor Module
Extracts GPS coordinates and metadata from image EXIF data.
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ExifExtractor:
    """Extracts GPS and metadata from image EXIF data."""
    
    @staticmethod
    def extract_gps(image_path: Path) -> Optional[Dict]:
        """
        Extract GPS coordinates from image EXIF data.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with GPS data or None if not available
            {
                'latitude': float,
                'longitude': float,
                'altitude': float (optional),
                'timestamp': str (optional),
                'camera_make': str (optional),
                'camera_model': str (optional)
            }
        """
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if not exif_data:
                logger.info(f"No EXIF data found in {image_path.name}")
                return None
            
            # Parse EXIF tags
            exif_dict = {}
            gps_info = {}
            
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                if tag_name == "GPSInfo":
                    # Parse GPS information
                    for gps_tag_id, gps_value in value.items():
                        gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag_name] = gps_value
                else:
                    exif_dict[tag_name] = value
            
            if not gps_info:
                logger.info(f"No GPS data found in EXIF for {image_path.name}")
                return None
            
            # Extract GPS coordinates
            latitude = ExifExtractor._convert_gps_coordinate(
                gps_info.get('GPSLatitude'),
                gps_info.get('GPSLatitudeRef')
            )
            
            longitude = ExifExtractor._convert_gps_coordinate(
                gps_info.get('GPSLongitude'),
                gps_info.get('GPSLongitudeRef')
            )
            
            if latitude is None or longitude is None:
                logger.warning(f"Invalid GPS coordinates in {image_path.name}")
                return None
            
            # Build result dictionary
            result = {
                'latitude': latitude,
                'longitude': longitude,
            }
            
            # Optional fields
            if 'GPSAltitude' in gps_info:
                altitude = ExifExtractor._convert_altitude(gps_info['GPSAltitude'])
                if altitude:
                    result['altitude'] = altitude
            
            if 'GPSDateStamp' in gps_info and 'GPSTimeStamp' in gps_info:
                result['gps_timestamp'] = f"{gps_info['GPSDateStamp']} {gps_info['GPSTimeStamp']}"
            
            if 'Make' in exif_dict:
                result['camera_make'] = str(exif_dict['Make'])
            
            if 'Model' in exif_dict:
                result['camera_model'] = str(exif_dict['Model'])
            
            if 'DateTime' in exif_dict:
                result['photo_timestamp'] = str(exif_dict['DateTime'])
            
            logger.info(f"✓ Extracted GPS: ({latitude:.6f}, {longitude:.6f})")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting EXIF data: {str(e)}")
            return None
    
    @staticmethod
    def _convert_gps_coordinate(coord: Optional[tuple], ref: Optional[str]) -> Optional[float]:
        """
        Convert GPS coordinate from degrees/minutes/seconds to decimal degrees.
        
        Args:
            coord: Tuple of (degrees, minutes, seconds)
            ref: Reference direction ('N', 'S', 'E', 'W')
            
        Returns:
            Decimal degrees or None if invalid
        """
        if not coord or not ref:
            return None
        
        try:
            # Extract degrees, minutes, seconds
            degrees = float(coord[0])
            minutes = float(coord[1])
            seconds = float(coord[2])
            
            # Convert to decimal degrees
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Apply direction (S and W are negative)
            if ref in ['S', 'W']:
                decimal = -decimal
            
            return decimal
            
        except (IndexError, ValueError, TypeError) as e:
            logger.error(f"Error converting GPS coordinate: {str(e)}")
            return None
    
    @staticmethod
    def _convert_altitude(altitude: Optional[tuple]) -> Optional[float]:
        """
        Convert altitude from EXIF format to float.
        
        Args:
            altitude: Altitude value from EXIF
            
        Returns:
            Altitude in meters or None
        """
        if not altitude:
            return None
        
        try:
            if isinstance(altitude, tuple):
                return float(altitude[0]) / float(altitude[1])
            return float(altitude)
        except (ValueError, TypeError, ZeroDivisionError):
            return None
    
    @staticmethod
    def has_gps_data(image_path: Path) -> bool:
        """
        Quick check if image contains GPS data.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if GPS data exists, False otherwise
        """
        gps_data = ExifExtractor.extract_gps(image_path)
        return gps_data is not None

