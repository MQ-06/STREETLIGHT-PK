"""
Model Loader Utility
Handles loading trained PyTorch models for inference.
"""

import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """Utility class for loading trained models."""
    
    def __init__(self, model_path: Path, device: Optional[str] = None):
        """
        Initialize model loader.
        
        Args:
            model_path: Path to model checkpoint (.pth file)
            device: Device to load model on ('cuda'/'cpu', auto-detect if None)
        """
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        logger.info(f"Using device: {self.device}")
        
        # Load checkpoint
        self.checkpoint = torch.load(self.model_path, map_location=self.device)
        
        # Load model
        self.model = self._create_model()
        self.model.eval()  # Set to evaluation mode
        
        # Get metadata
        self.class_to_idx = self.checkpoint['class_to_idx']
        self.idx_to_class = self.checkpoint['idx_to_class']
        self.num_classes = self.checkpoint['config']['num_classes']
        self.val_accuracy = self.checkpoint['val_accuracy']
        self.training_config = self.checkpoint['config']
        
        logger.info(f"✓ Model loaded successfully")
        logger.info(f"  Classes: {list(self.class_to_idx.keys())}")
        logger.info(f"  Val Accuracy: {self.val_accuracy:.2f}%")
    
    def _create_model(self) -> nn.Module:
        """
        Create model architecture and load weights.
        
        Returns:
            Loaded model
        """
        # Create ResNet18 architecture
        model = models.resnet18(pretrained=False)
        
        # Modify final layer
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, self.checkpoint['config']['num_classes'])
        
        # Load trained weights
        model.load_state_dict(self.checkpoint['model_state_dict'])
        
        # Move to device
        model = model.to(self.device)
        
        return model
    
    def get_model(self) -> nn.Module:
        """
        Get loaded model.
        
        Returns:
            PyTorch model
        """
        return self.model
    
    def get_class_names(self) -> Dict[int, str]:
        """
        Get class index to name mapping.
        
        Returns:
            Dictionary mapping indices to class names
        """
        return {int(k): v for k, v in self.idx_to_class.items()}
    
    def get_metadata(self) -> Dict:
        """
        Get model metadata.
        
        Returns:
            Dictionary containing model information
        """
        return {
            'model_name': 'ResNet18',
            'num_classes': self.num_classes,
            'classes': list(self.class_to_idx.keys()),
            'val_accuracy': self.val_accuracy,
            'device': str(self.device),
            'training_config': self.training_config
        }
