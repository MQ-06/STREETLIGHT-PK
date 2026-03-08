"""
Engine E: Final Confidence Score (Layer 5)

Combines the AI classification score (Layer 1), community verification score
(Layer 3), and trust history score (Layer 4) into a single combined_score
(0-100) and assigns a verification_status to the report.

Decision thresholds:
    85-100  →  AUTO_VERIFIED
    60-84   →  REVIEW_NEEDED
    0-59    →  REJECTED

When community_score is None (no votes collected yet), adjusted weights are
used so the score remains meaningful without community input.
"""
from .score_calculator import FinalScoreCalculator

__all__ = ["FinalScoreCalculator"]
