"""Minimal model load + forward (duplicated from backend for standalone deploy)."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

logger = logging.getLogger(__name__)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
IMAGE_SIZE = 224
TEMPERATURE = 1.0


class StreetlightClassifier:
    def __init__(self, model_path: Path | None = None):
        from model_loader import ModelLoader

        if model_path is None:
            layer_root = Path(__file__).resolve().parent / "models"
            model_path = layer_root / "best_model.pth"
        self.loader = ModelLoader(model_path)
        self.model = self.loader.get_model()
        self.device = self.loader.device
        self.class_names: List[str] = [
            self.loader.idx_to_class[i] for i in sorted(self.loader.idx_to_class.keys())
        ]
        self.transform = transforms.Compose(
            [
                transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
                transforms.ToTensor(),
                transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ]
        )

    def predict_image_bytes(self, data: bytes) -> Dict:
        image_pil = Image.open(__import__("io").BytesIO(data)).convert("RGB")
        return self._predict_pil(image_pil)

    def _predict_pil(self, image_pil: Image.Image) -> Dict:
        image_tensor = self.transform(image_pil).unsqueeze(0).to(self.device)
        name_to_idx = {name: i for i, name in enumerate(self.class_names)}
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = F.softmax(outputs / TEMPERATURE, dim=1)[0]

        confidence_value, pred_idx = torch.max(probabilities, dim=0)
        confidence_value = float(confidence_value.item())
        predicted_class = self.class_names[int(pred_idx.item())]

        pb = (
            probabilities[name_to_idx["pothole"]].item()
            if "pothole" in name_to_idx
            else 0.0
        )
        pg = (
            probabilities[name_to_idx["garbage"]].item()
            if "garbage" in name_to_idx
            else 0.0
        )
        if predicted_class == "other":
            best_civic = "pothole" if pb >= pg else "garbage"
            best_p = max(pb, pg)
            if best_p >= 0.14 and confidence_value < 0.82:
                ci = name_to_idx[best_civic]
                predicted_class = best_civic
                confidence_value = float(probabilities[ci].item())
                pred_idx = torch.tensor(ci, device=probabilities.device, dtype=torch.long)

        all_probs = {
            self.class_names[i]: float(probabilities[i].item() * 100)
            for i in range(len(self.class_names))
        }
        conf_threshold = float(os.getenv("CLASSIFIER_CONFIDENCE_THRESHOLD", "0.68"))
        is_valid_issue = predicted_class != "other" and confidence_value >= conf_threshold

        return {
            "predicted_class": predicted_class,
            "confidence": round(confidence_value * 100, 2),
            "confidence_raw": confidence_value,
            "all_probabilities": {k: round(v, 2) for k, v in all_probs.items()},
            "is_valid_issue": is_valid_issue,
        }
