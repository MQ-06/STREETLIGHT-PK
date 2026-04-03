# backend/services/routing/city_detector.py
"""
Detects which city a GPS coordinate belongs to by checking
it against the bounding boxes defined in agent_config.CITIES.

Returns the city slug ("lahore" | "faisalabad") or None if
the coordinate falls outside all known city boundaries.
"""

import logging
from typing import Optional

from agents.agent_config import CITIES

logger = logging.getLogger(__name__)


def detect_city(lat: float, lng: float) -> Optional[str]:
    """
    Check lat/lng against all city bounding boxes.

    Returns:
        City slug string (e.g. "lahore") if inside a known boundary,
        None if the coordinate is outside all configured cities.
    """
    if lat is None or lng is None:
        logger.warning("city_detector: received None coordinates")
        return None

    for city_slug, bounds in CITIES.items():
        if (
            bounds["lat_min"] <= lat <= bounds["lat_max"]
            and bounds["lng_min"] <= lng <= bounds["lng_max"]
        ):
            logger.info(
                f"🗺️  city_detector: ({lat:.4f}, {lng:.4f}) → {city_slug}"
            )
            return city_slug

    logger.info(
        f"🗺️  city_detector: ({lat:.4f}, {lng:.4f}) → no match "
        f"(outside all {len(CITIES)} configured cities)"
    )
    return None


def get_city_display_name(city_slug: str) -> str:
    """Returns human-readable city name for a slug, e.g. 'lahore' → 'Lahore'."""
    city = CITIES.get(city_slug)
    return city["display_name"] if city else city_slug.title()
