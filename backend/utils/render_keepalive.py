"""
Optional HTTP ping to this service's public URL (e.g. Render free tier).

Set SELF_PING_BASE_URL on the server (e.g. https://your-app.onrender.com).
Scheduled from agent_scheduler; no-op if env is unset (local dev).
"""
from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)


def run_keepalive_ping() -> None:
    base = (os.getenv("SELF_PING_BASE_URL") or "").strip().rstrip("/")
    if not base:
        return
    path = (os.getenv("SELF_PING_PATH") or "/health").strip() or "/health"
    if not path.startswith("/"):
        path = "/" + path
    url = f"{base}{path}"
    timeout = float(os.getenv("SELF_PING_TIMEOUT_SECONDS", "25"))
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.get(url)
        if r.status_code == 200:
            logger.debug("Keepalive ping OK: %s", url)
        else:
            logger.warning("Keepalive ping %s returned %s", url, r.status_code)
    except Exception as e:
        logger.warning("Keepalive ping failed (%s): %s", url, e)
