# backend/agents/agent_config.py
"""
Central configuration for the agentic AI system.
All thresholds, city boundaries, department mappings, and routing
constants live here. To add a new city: add one entry to CITIES and
add rows to CITY_DEPT_MAP. No other code changes needed.
"""

# ================================================================
# CITY BOUNDING BOXES
# Format: lat_min, lat_max, lng_min, lng_max (WGS-84 decimal degrees)
# ================================================================
CITIES: dict[str, dict] = {
    "lahore": {
        "lat_min":      31.41,
        "lat_max":      31.65,
        "lng_min":      74.17,
        "lng_max":      74.45,
        "display_name": "Lahore",
        "city_admin_email": "lahore_ca@streetlight.local",
    },
    "faisalabad": {
        "lat_min":      31.30,
        "lat_max":      31.52,
        "lng_min":      72.95,
        "lng_max":      73.20,
        "display_name": "Faisalabad",
        "city_admin_email": "faisalabad_ca@streetlight.local",
    },
}

# ================================================================
# DEPARTMENT REGISTRY
# key   → internal slug used in DB and routing logic
# value → human-readable full name shown in admin UI
# ================================================================
DEPARTMENTS: dict[str, str] = {
    "lmc":  "Lahore Metropolitan Corporation",
    "lwmc": "Lahore Waste Management Company",
    "fmc":  "Faisalabad Metropolitan Corporation",
    "fwmc": "Faisalabad Waste Management Company",
}

# ================================================================
# ISSUE TYPE → DEPARTMENT MAPPING (city-aware)
# Keys: (city_slug, ai_predicted_class_lowercase)
# Values: department slug from DEPARTMENTS
#
# IssueCategory values from the model are POTHOLE and TRASH.
# The AI classifier returns "pothole" or "garbage".
# Both are mapped here for safety.
# ================================================================
CITY_DEPT_MAP: dict[tuple[str, str], str] = {
    ("lahore",     "pothole"): "lmc",
    ("lahore",     "garbage"): "lwmc",
    ("lahore",     "trash"):   "lwmc",    # alias — IssueCategory.TRASH
    ("faisalabad", "pothole"): "fmc",
    ("faisalabad", "garbage"): "fwmc",
    ("faisalabad", "trash"):   "fwmc",    # alias — IssueCategory.TRASH
}

# ================================================================
# AGENTIC AI THRESHOLDS  (used by agent_rules.py in Phase 4)
# ================================================================

# Layer 5 combined_score thresholds
SCORE_AUTO_VERIFY   = 85   # ≥ this → auto-verify, route to officer
SCORE_REVIEW_NEEDED = 60   # between this and AUTO_VERIFY → officer reviews
SCORE_REJECT        = 60   # < this → reject

# Community verification
MIN_COMMUNITY_VOTES_TO_VERIFY = 3   # votes needed to advance past PENDING_VERIFICATION

# Escalation
STALL_HOURS_IN_PROGRESS = 48    # hours before escalation fires
AUTO_CLOSE_DAYS         = 7     # days with no citizen rejection → auto-resolve

# Field worker token TTL
FIELD_WORKER_TOKEN_TTL_HOURS = 72

# After-photo GPS tolerance (metres)
AFTER_PHOTO_GPS_TOLERANCE_M = 50

# ================================================================
# ROLE CONSTANTS  (mirrors rbac.py — single source of truth here)
# ================================================================
ROLE_SUPER_ADMIN  = "super_admin"
ROLE_CITY_ADMIN   = "city_admin"
ROLE_DEPT_OFFICER = "dept_officer"

ADMIN_ROLES = {ROLE_SUPER_ADMIN, ROLE_CITY_ADMIN, ROLE_DEPT_OFFICER}
