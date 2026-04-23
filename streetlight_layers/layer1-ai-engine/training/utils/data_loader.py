"""
Data Loading and Augmentation Utilities
Provides PyTorch DataLoaders with appropriate transforms for training and validation.
"""

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from pathlib import Path
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)

# ImageNet normalization values (standard for pre-trained models)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Image size for ResNet input
IMAGE_SIZE = 224


def get_train_transforms() -> transforms.Compose:
    """
    Get training data transforms with augmentation.
    
    Augmentation techniques:
    - Resize to 224x224 (ResNet input size)
    - Random horizontal flip
    - Random rotation (±15 degrees)
    - Color jitter (brightness, contrast, saturation)
    - Convert to tensor
    - Normalize using ImageNet mean/std
    
    Returns:
        Composed transforms for training
    """
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(
            brightness=0.2,
            contrast=0.2,
            saturation=0.2,
            hue=0.1
        ),
        transforms.RandomAffine(
            degrees=0,
            translate=(0.1, 0.1),
            scale=(0.9, 1.1)
        ),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])


def get_val_transforms() -> transforms.Compose:
    """
    Get validation/test data transforms without augmentation.
    
    Only includes:
    - Resize to 224x224
    - Convert to tensor
    - Normalize using ImageNet mean/std
    
    Returns:
        Composed transforms for validation
    """
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])


def get_data_loaders(
    train_dir: Path,
    val_dir: Path,
    batch_size: int = 32,
    num_workers: int = 4
) -> Tuple[DataLoader, DataLoader, Dict[str, int]]:
    """
    Create PyTorch DataLoaders for training and validation.
    
    Args:
        train_dir: Path to training data directory
        val_dir: Path to validation data directory
        batch_size: Batch size for DataLoader
        num_workers: Number of worker processes for data loading
        
    Returns:
        Tuple of (train_loader, val_loader, class_to_idx)
    """
    # Get transforms
    train_transforms = get_train_transforms()
    val_transforms = get_val_transforms()
    
    # Create datasets
    logger.info(f"Loading training data from: {train_dir}")
    train_dataset = datasets.ImageFolder(
        root=train_dir,
        transform=train_transforms
    )
    
    logger.info(f"Loading validation data from: {val_dir}")
    val_dataset = datasets.ImageFolder(
        root=val_dir,
        transform=val_transforms
    )
    
    # Get class information
    class_to_idx = train_dataset.class_to_idx
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    
    logger.info(f"Classes found: {list(class_to_idx.keys())}")
    logger.info(f"Training samples: {len(train_dataset)}")
    logger.info(f"Validation samples: {len(val_dataset)}")
    
    # Create DataLoaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    logger.info(f"Train batches: {len(train_loader)}")
    logger.info(f"Val batches: {len(val_loader)}")
    
    return train_loader, val_loader, class_to_idx


def get_class_distribution(data_loader: DataLoader) -> Dict[str, int]:
    """
    Calculate class distribution in a dataset.
    
    Args:
        data_loader: PyTorch DataLoader
        
    Returns:
        Dictionary mapping class indices to counts
    """
    class_counts = {}
    
    for _, labels in data_loader:
        for label in labels:
            label_idx = label.item()
            class_counts[label_idx] = class_counts.get(label_idx, 0) + 1
    
    return class_counts


def denormalize_image(tensor: torch.Tensor) -> torch.Tensor:
    """
    Denormalize an image tensor for visualization.
    
    Args:
        tensor: Normalized image tensor
        
    Returns:
        Denormalized tensor
    """
    mean = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
    std = torch.tensor(IMAGENET_STD).view(3, 1, 1)
    
    return tensor * std + mean

