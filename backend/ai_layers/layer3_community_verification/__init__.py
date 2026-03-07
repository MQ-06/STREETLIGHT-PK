"""
Engine C: Community Verification (Layer 3)

Handles the full lifecycle of community-driven report verification:
  - Creates VerificationRequests linked to newly submitted reports
  - Collects weighted YES / NO votes from nearby users
  - Calculates a Community Confidence Score (0–100) once the vote threshold is met
  - Expires stale requests and finalises partial scores (or leaves NULL if no votes)
"""

from .community_engine import CommunityVerificationEngine

__all__ = ["CommunityVerificationEngine"]
