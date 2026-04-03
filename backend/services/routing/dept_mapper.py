# backend/services/routing/dept_mapper.py
"""
Maps (city, issue_type) → department slug.

issue_type is the AI-predicted class (lowercase): "pothole" | "garbage"
It also handles "trash" as an alias for IssueCategory.TRASH.

Returns the department slug (e.g. "lmc", "lwmc", "fmc", "fwmc")
or None if no mapping exists for this combination.
"""

import logging
from typing import Optional

from agents.agent_config import CITY_DEPT_MAP, DEPARTMENTS

logger = logging.getLogger(__name__)


def map_issue_to_department(city: str, issue_type: str) -> Optional[str]:
    """
    Args:
        city:       City slug, e.g. "lahore"
        issue_type: Lowercased AI class, e.g. "pothole" or "garbage"

    Returns:
        Department slug string or None if mapping not found.
    """
    if not city or not issue_type:
        return None

    key = (city.lower().strip(), issue_type.lower().strip())
    dept = CITY_DEPT_MAP.get(key)

    if dept:
        display = DEPARTMENTS.get(dept, dept)
        logger.info(f"🏢 dept_mapper: {key} → {dept} ({display})")
    else:
        logger.warning(f"⚠️  dept_mapper: no mapping for {key}")

    return dept


def get_department_display_name(dept_slug: str) -> str:
    """Returns full authority name for a department slug."""
    return DEPARTMENTS.get(dept_slug, dept_slug.upper())
