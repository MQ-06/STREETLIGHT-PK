"""
Model Loader Utility
Handles loading trained PyTorch models for inference.
"""

import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)


class ModelLoader:
    """Utility class for loading trained EfficientNet-B3 models."""

    def __init__(self, model_path: Path, device: Optional[str] = None):
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            logger.info("Model file not found locally — downloading from Hugging Face Hub...")
            self._download_from_hub()

        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        logger.info(f"Using device: {self.device}")

        self.checkpoint = torch.load(self.model_path, map_location=self.device)

        self.class_to_idx = self.checkpoint['class_to_idx']
        self.idx_to_class = {int(k): v for k, v in self.checkpoint['idx_to_class'].items()}
        self.num_classes  = len(self.class_to_idx)
        self.model_name   = self.checkpoint.get('model_name', 'efficientnet_b3')

        self.model = self._create_model()
        self.model.eval()

        logger.info(f"Model loaded: {self.model_name}")
        logger.info(f"Classes: {list(self.class_to_idx.keys())}")

    def _download_from_hub(self):
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            raise ImportError("huggingface_hub is required. Run: pip install huggingface_hub")

        repo_id = os.getenv("HF_REPO_ID")
        if not repo_id:
            raise EnvironmentError("HF_REPO_ID env var not set (e.g. 'your-username/streetlight-model')")

        token = os.getenv("HF_TOKEN", None)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        hf_hub_download(
            repo_id=repo_id,
            filename="best_model.pth",
            token=token,
            local_dir=str(self.model_path.parent),
        )
        logger.info(f"Model downloaded to {self.model_path}")

    def _create_model(self) -> nn.Module:
        try:
            import timm
        except ImportError:
            raise ImportError("timm is required. Run: pip install timm")

        model = timm.create_model(
            self.model_name,
            pretrained=False,
            num_classes=self.num_classes
        )
        model.load_state_dict(self.checkpoint['model_state_dict'])
        model = model.to(self.device)
        return model

    def get_model(self) -> nn.Module:
        return self.model

    def get_class_names(self) -> Dict[int, str]:
        return self.idx_to_class

    def get_metadata(self) -> Dict:
        return {
            'model_name'  : self.model_name,
            'num_classes' : self.num_classes,
            'classes'     : list(self.class_to_idx.keys()),
            'device'      : str(self.device),
        }
