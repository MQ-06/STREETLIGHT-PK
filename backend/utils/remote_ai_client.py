"""HTTP client for remote StreetLight classifier (HF Space / VM)."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


def fetch_remote_classification(
    base_url: str,
    image_path: str,
    *,
    token: Optional[str] = None,
    timeout_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    """
    POST image to {base_url}/predict (multipart field "file").
    """
    base = base_url.rstrip("/")
    url = f"{base}/predict"
    t = timeout_seconds or float(os.getenv("AI_INFERENCE_TIMEOUT_SECONDS", "120"))
    path = Path(image_path)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    mime = "application/octet-stream"
    suf = path.suffix.lower()
    if suf in (".jpg", ".jpeg"):
        mime = "image/jpeg"
    elif suf == ".png":
        mime = "image/png"

    with open(path, "rb") as f:
        files = {"file": (path.name, f, mime)}
        with httpx.Client(timeout=t) as client:
            r = client.post(url, files=files, headers=headers)

    if r.status_code >= 400:
        logger.error("Remote AI error %s: %s", r.status_code, r.text[:500])
        r.raise_for_status()

    data = r.json()
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(data.get("error", "remote error"))
    return data
