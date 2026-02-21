"""
Geocoder Module
Converts GPS coordinates to human-readable addresses using OpenStreetMap Nominatim API.
"""

import requests
import time
import logging
from typing import Optional, Dict, Tuple
from .config import (
    NOMINATIM_API_URL,
    USER_AGENT,
    GEOCODING_TIMEOUT,
    NOMINATIM_DELAY
)

logger = logging.getLogger(__name__)


class Geocoder:
    """Handles reverse geocoding using OpenStreetMap Nominatim API."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.last_request_time = 0
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Convert GPS coordinates to address using Nominatim API.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dictionary with address information or None if failed
            {
                'display_name': str,      # Full address
                'road': str,              # Street name
                'suburb': str,            # Neighborhood/suburb
                'city': str,              # City name
                'state': str,             # State/province
                'country': str,           # Country
                'postcode': str,          # Postal code
                'lat': str,               # Latitude
                'lon': str                # Longitude
            }
        """
        # Validate coordinates
        if not self._is_valid_coordinate(latitude, longitude):
            logger.error(f"Invalid coordinates: ({latitude}, {longitude})")
            return None
        
        # Rate limiting (Nominatim requires 1 second between requests)
        self._respect_rate_limit()
        
        try:
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1,
                'zoom': 18  # Street-level detail
            }
            
            logger.info(f"Geocoding: ({latitude:.6f}, {longitude:.6f})")
            
            response = self.session.get(
                NOMINATIM_API_URL,
                params=params,
                timeout=GEOCODING_TIMEOUT
            )
            
            response.raise_for_status()
            data = response.json()
            
            if not data or 'error' in data:
                logger.warning(f"Geocoding failed: {data.get('error', 'Unknown error')}")
                return None
            
            # Parse address components
            address = data.get('address', {})
            
            result = {
                'display_name': data.get('display_name', 'Unknown location'),
                'road': address.get('road', address.get('highway', '')),
                'suburb': address.get('suburb', address.get('neighbourhood', '')),
                'city': address.get('city', address.get('town', address.get('village', ''))),
                'state': address.get('state', address.get('province', '')),
                'country': address.get('country', ''),
                'postcode': address.get('postcode', ''),
                'lat': data.get('lat', str(latitude)),
                'lon': data.get('lon', str(longitude))
            }
            
            logger.info(f"✓ Geocoded: {result['display_name'][:80]}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Geocoding request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
            return None
    
    def get_short_address(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Get shortened address string for display.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Short address string (e.g., "Mall Road, Lahore, Punjab")
        """
        address_data = self.reverse_geocode(latitude, longitude)
        
        if not address_data:
            return None
        
        # Build short address from available components
        parts = []
        
        if address_data.get('road'):
            parts.append(address_data['road'])
        
        if address_data.get('suburb'):
            parts.append(address_data['suburb'])
        elif address_data.get('city'):
            parts.append(address_data['city'])
        
        if address_data.get('state'):
            parts.append(address_data['state'])
        
        return ', '.join(parts) if parts else address_data.get('display_name', 'Unknown')
    
    def _is_valid_coordinate(self, latitude: float, longitude: float) -> bool:
        """
        Validate GPS coordinates.
        
        Args:
            latitude: Latitude value
            longitude: Longitude value
            
        Returns:
            True if valid, False otherwise
        """
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            # Check ranges
            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lon <= 180):
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    def _respect_rate_limit(self):
        """
        Ensure minimum delay between API requests.
        Nominatim requires 1 second between requests.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < NOMINATIM_DELAY:
            sleep_time = NOMINATIM_DELAY - time_since_last_request
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

