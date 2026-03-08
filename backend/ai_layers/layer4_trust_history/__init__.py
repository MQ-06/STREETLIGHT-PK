"""
Engine D: Trust History (Layer 4)

Evaluates user trustworthiness and produces a Trust Score (0-100) based on
four weighted sub-scores: account age, report history, fraud history, and
recent behaviour.

is_trusted = True when trust_score >= 40.
"""
from .trust_engine import TrustHistoryEngine

__all__ = ["TrustHistoryEngine"]
