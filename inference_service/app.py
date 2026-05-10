"""
StreetLight remote classifier — deploy on Hugging Face Spaces (Docker) or any host.
POST /predict  multipart field "file" (image)
GET  /health
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, File, Header, UploadFile
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="StreetLight Classifier", version="1.0.0")
_classifier = None


def _check_token(authorization: str | None) -> None:
    expected = (os.getenv("INFERENCE_API_TOKEN") or "").strip()
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise PermissionError("Missing bearer token")
    if authorization[7:].strip() != expected:
        raise PermissionError("Invalid token")


def get_classifier():
    global _classifier
    if _classifier is None:
        from model_core import StreetlightClassifier

        models_dir = Path(__file__).resolve().parent / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        model_path = models_dir / "best_model.pth"
        _classifier = StreetlightClassifier(model_path=model_path)
    return _classifier


@app.on_event("startup")
async def startup():
    logger.info("Loading classifier...")
    get_classifier()
    logger.info("Classifier ready.")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "streetlight-inference"}


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    authorization: str | None = Header(None),
):
    try:
        try:
            _check_token(authorization)
        except PermissionError as e:
            return JSONResponse({"error": str(e)}, status_code=401)
        data = await file.read()
        if not data:
            return JSONResponse({"error": "empty file"}, status_code=400)
        result = get_classifier().predict_image_bytes(data)
        return result
    except Exception as e:
        logger.exception("predict failed")
        return JSONResponse({"error": str(e)}, status_code=500)
