"""
Landmark Finder Module
Finds nearby points of interest using OpenStreetMap Overpass API.
"""

import requests
import logging
from typing import List, Dict, Optional, Tuple
from .config import (
    OVERPASS_API_URL,
    USER_AGENT,
    LANDMARK_TIMEOUT,
    LANDMARK_SEARCH_RADIUS_M,
    MAX_LANDMARKS_RETURN,
    LANDMARK_CATEGORIES
)

logger = logging.getLogger(__name__)


class LandmarkFinder:
    """Finds nearby landmarks and points of interest using Overpass API."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def find_nearby_landmarks(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = LANDMARK_SEARCH_RADIUS_M
    ) -> List[Dict]:
        """
        Find nearby landmarks within specified radius.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_meters: Search radius in meters (default: 500m)
            
        Returns:
            List of landmark dictionaries, each containing:
            {
                'name': str,
                'type': str,
                'category': str,
                'distance_m': float,
                'lat': float,
                'lon': float
            }
        """
        try:
            # Build Overpass QL query
            query = self._build_overpass_query(latitude, longitude, radius_meters)
            
            logger.info(f"Searching landmarks within {radius_meters}m of ({latitude:.6f}, {longitude:.6f})")
            
            response = self.session.post(
                OVERPASS_API_URL,
                data={'data': query},
                timeout=LANDMARK_TIMEOUT
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse results
            landmarks = self._parse_overpass_results(data, latitude, longitude)
            
            # Sort by distance
            landmarks.sort(key=lambda x: x['distance_m'])
            
            # Return top N landmarks
            top_landmarks = landmarks[:MAX_LANDMARKS_RETURN]
            
            logger.info(f"✓ Found {len(top_landmarks)} landmarks")
            return top_landmarks
            
        except requests.exceptions.Timeout:
            logger.error("Landmark search timed out")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Landmark search request failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Landmark search error: {str(e)}")
            return []
    
    def _build_overpass_query(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int
    ) -> str:
        """
        Build Overpass QL query for finding nearby landmarks.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Search radius
            
        Returns:
            Overpass QL query string
        """
        # Query for various landmark types within radius
        query = f"""
        [out:json][timeout:15];
        (
          node["name"]["amenity"](around:{radius_meters},{latitude},{longitude});
          node["name"]["shop"](around:{radius_meters},{latitude},{longitude});
          node["name"]["building"](around:{radius_meters},{latitude},{longitude});
          way["name"]["amenity"](around:{radius_meters},{latitude},{longitude});
          way["name"]["shop"](around:{radius_meters},{latitude},{longitude});
          way["name"]["building"](around:{radius_meters},{latitude},{longitude});
          way["name"]["highway"](around:{radius_meters},{latitude},{longitude});
        );
        out center {MAX_LANDMARKS_RETURN * 2};
        """
        return query.strip()
    
    def _parse_overpass_results(
        self,
        data: Dict,
        center_lat: float,
        center_lon: float
    ) -> List[Dict]:
        """
        Parse Overpass API results into landmark dictionaries.
        
        Args:
            data: Overpass API response
            center_lat: Center latitude for distance calculation
            center_lon: Center longitude for distance calculation
            
        Returns:
            List of parsed landmarks
        """
        landmarks = []
        elements = data.get('elements', [])
        
        for element in elements:
            try:
                # Get name
                name = element.get('tags', {}).get('name')
                if not name:
                    continue
                
                # Get coordinates
                if element['type'] == 'node':
                    lat = element.get('lat')
                    lon = element.get('lon')
                elif element['type'] == 'way' and 'center' in element:
                    lat = element['center'].get('lat')
                    lon = element['center'].get('lon')
                else:
                    continue
                
                if lat is None or lon is None:
                    continue
                
                # Calculate distance
                distance_m = self._calculate_distance_meters(
                    center_lat, center_lon,
                    lat, lon
                )
                
                # Get landmark type/category
                tags = element.get('tags', {})
                landmark_type, category = self._get_landmark_type(tags)
                
                landmarks.append({
                    'name': name,
                    'type': landmark_type,
                    'category': category,
                    'distance_m': round(distance_m, 1),
                    'lat': lat,
                    'lon': lon
                })
                
            except Exception as e:
                logger.debug(f"Error parsing landmark element: {str(e)}")
                continue
        
        return landmarks
    
    def _get_landmark_type(self, tags: Dict) -> Tuple[str, str]:
        """
        Determine landmark type and category from OSM tags.
        
        Args:
            tags: OSM tags dictionary
            
        Returns:
            Tuple of (type_name, category)
        """
        # Priority order for categories
        for category in LANDMARK_CATEGORIES:
            if category in tags:
                type_value = tags[category]
                return (type_value, category)
        
        return ('unknown', 'other')
    
    def _calculate_distance_meters(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two points using simple approximation.
        Good enough for small distances (< 1km).
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Convert to radians
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Earth radius in meters
        earth_radius_m = 6371000
        distance = earth_radius_m * c
        
        return distance
    
    def has_landmarks_nearby(
        self,
        latitude: float,
        longitude: float,
        min_landmarks: int = 1
    ) -> bool:
        """
        Check if location has nearby landmarks.
        
        Args:
            latitude: Latitude to check
            longitude: Longitude to check
            min_landmarks: Minimum number of landmarks required
            
        Returns:
            True if sufficient landmarks found
        """
        landmarks = self.find_nearby_landmarks(latitude, longitude)
        return len(landmarks) >= min_landmarks

