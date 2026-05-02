"""
Training Script for StreetLight AI Image Classifier
Trains ResNet18 model to classify images as pothole, garbage, or other.

Usage:
    python train.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torchvision import models
from pathlib import Path
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
import logging
from tqdm import tqdm

from utils.data_loader import get_data_loaders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set random seeds for reproducibility
RANDOM_SEED = 42
torch.manual_seed(RANDOM_SEED)
torch.cuda.manual_seed_all(RANDOM_SEED)
import numpy as np
import random
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Training configuration
CONFIG = {
    'model_name': 'resnet18',
    'num_classes': 3,
    'batch_size': 32,
    'num_epochs': 25,
    'learning_rate': 0.001,
    'num_workers': 4,
    'early_stopping_patience': 5,
    'random_seed': RANDOM_SEED,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}

# Paths
DATA_DIR = Path(__file__).parent / "data"
TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "val"
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


def create_model(num_classes: int, pretrained: bool = True) -> nn.Module:
    """
    Create ResNet18 model with modified final layer for our classes.
    
    Args:
        num_classes: Number of output classes
        pretrained: Whether to use ImageNet pretrained weights
        
    Returns:
        Modified ResNet18 model
    """
    logger.info(f"Creating ResNet18 model (pretrained={pretrained})")
    
    # Load pretrained ResNet18
    model = models.resnet18(pretrained=pretrained)
    
    # Modify final fully connected layer
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    
    logger.info(f"Model output layer: {num_features} -> {num_classes} classes")
    
    return model


def train_one_epoch(
    model: nn.Module,
    train_loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
    epoch: int
) -> Tuple[float, float]:
    """
    Train model for one epoch.
    
    Args:
        model: PyTorch model
        train_loader: Training data loader
        criterion: Loss function
        optimizer: Optimizer
        device: Device (cuda/cpu)
        epoch: Current epoch number
        
    Returns:
        Tuple of (average_loss, accuracy)
    """
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    # Progress bar
    pbar = tqdm(train_loader, desc=f"Epoch {epoch} [Train]")
    
    for batch_idx, (inputs, labels) in enumerate(pbar):
        inputs, labels = inputs.to(device), labels.to(device)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Statistics
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        # Update progress bar
        avg_loss = running_loss / (batch_idx + 1)
        accuracy = 100.0 * correct / total
        pbar.set_postfix({
            'loss': f'{avg_loss:.4f}',
            'acc': f'{accuracy:.2f}%'
        })
    
    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100.0 * correct / total
    
    return epoch_loss, epoch_acc


def validate(
    model: nn.Module,
    val_loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
    epoch: int
) -> Tuple[float, float]:
    """
    Validate model on validation set.
    
    Args:
        model: PyTorch model
        val_loader: Validation data loader
        criterion: Loss function
        device: Device (cuda/cpu)
        epoch: Current epoch number
        
    Returns:
        Tuple of (average_loss, accuracy)
    """
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(val_loader, desc=f"Epoch {epoch} [Val]  ")
    
    with torch.no_grad():
        for batch_idx, (inputs, labels) in enumerate(pbar):
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # Statistics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            avg_loss = running_loss / (batch_idx + 1)
            accuracy = 100.0 * correct / total
            pbar.set_postfix({
                'loss': f'{avg_loss:.4f}',
                'acc': f'{accuracy:.2f}%'
            })
    
    epoch_loss = running_loss / len(val_loader)
    epoch_acc = 100.0 * correct / total
    
    return epoch_loss, epoch_acc


def save_checkpoint(
    model: nn.Module,
    optimizer: optim.Optimizer,
    epoch: int,
    val_acc: float,
    class_to_idx: Dict[str, int],
    config: Dict,
    filepath: Path
):
    """
    Save model checkpoint.
    
    Args:
        model: PyTorch model
        optimizer: Optimizer
        epoch: Current epoch
        val_acc: Validation accuracy
        class_to_idx: Class to index mapping
        config: Training configuration
        filepath: Path to save checkpoint
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'val_accuracy': val_acc,
        'class_to_idx': class_to_idx,
        'idx_to_class': {v: k for k, v in class_to_idx.items()},
        'config': config,
        'timestamp': datetime.now().isoformat()
    }
    
    torch.save(checkpoint, filepath)
    logger.info(f"✓ Checkpoint saved: {filepath}")


def main():
    """Main training function."""
    
    print("="*80)
    print("StreetLight AI Engine - Model Training")
    print("="*80)
    print()
    
    # Check if data directories exist
    if not TRAIN_DIR.exists() or not VAL_DIR.exists():
        logger.error("Training/validation data not found!")
        logger.error(f"Expected: {TRAIN_DIR} and {VAL_DIR}")
        logger.error("\nPlease run data preparation first:")
        logger.error("  python prepare_data.py")
        return
    
    # Device configuration
    device = torch.device(CONFIG['device'])
    logger.info(f"Using device: {device}")
    
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA Version: {torch.version.cuda}")
    
    # Load data
    logger.info("\n" + "-"*80)
    logger.info("Loading Data")
    logger.info("-"*80)
    
    train_loader, val_loader, class_to_idx = get_data_loaders(
        train_dir=TRAIN_DIR,
        val_dir=VAL_DIR,
        batch_size=CONFIG['batch_size'],
        num_workers=CONFIG['num_workers']
    )
    
    # Create model
    logger.info("\n" + "-"*80)
    logger.info("Creating Model")
    logger.info("-"*80)
    
    model = create_model(num_classes=CONFIG['num_classes'], pretrained=True)
    model = model.to(device)
    
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=CONFIG['learning_rate'])
    
    # Learning rate scheduler
    scheduler = ReduceLROnPlateau(
        optimizer,
        mode='max',
        factor=0.5,
        patience=3
    )
    
    # Training history
    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': [],
        'learning_rates': []
    }
    
    # Training loop
    logger.info("\n" + "-"*80)
    logger.info("Training")
    logger.info("-"*80)
    logger.info(f"Epochs: {CONFIG['num_epochs']}")
    logger.info(f"Batch size: {CONFIG['batch_size']}")
    logger.info(f"Learning rate: {CONFIG['learning_rate']}")
    logger.info(f"Early stopping patience: {CONFIG['early_stopping_patience']}")
    print()
    
    best_val_acc = 0.0
    epochs_without_improvement = 0
    start_time = time.time()
    
    for epoch in range(1, CONFIG['num_epochs'] + 1):
        # Train
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        
        # Validate
        val_loss, val_acc = validate(
            model, val_loader, criterion, device, epoch
        )
        
        # Update learning rate
        scheduler.step(val_acc)
        current_lr = optimizer.param_groups[0]['lr']
        
        # Save history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['learning_rates'].append(current_lr)
        
        # Print epoch summary
        print(f"\nEpoch {epoch}/{CONFIG['num_epochs']} Summary:")
        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
        print(f"  Learning Rate: {current_lr:.6f}")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            epochs_without_improvement = 0
            
            save_checkpoint(
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                val_acc=val_acc,
                class_to_idx=class_to_idx,
                config=CONFIG,
                filepath=MODELS_DIR / "best_model.pth"
            )
            print(f"  ✓ New best model! Val Acc: {val_acc:.2f}%")
        else:
            epochs_without_improvement += 1
            print(f"  No improvement for {epochs_without_improvement} epoch(s)")
        
        # Early stopping
        if epochs_without_improvement >= CONFIG['early_stopping_patience']:
            logger.info(f"\nEarly stopping triggered after {epoch} epochs")
            logger.info(f"Best validation accuracy: {best_val_acc:.2f}%")
            break
        
        print()
    
    # Training complete
    training_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("Training Complete!")
    print("="*80)
    print(f"Training time: {training_time/60:.2f} minutes")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved: {MODELS_DIR / 'best_model.pth'}")
    
    # Save training history
    history_file = MODELS_DIR / "training_history.json"
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    logger.info(f"Training history saved: {history_file}")
    
    # Save final configuration
    config_file = MODELS_DIR / "training_config.json"
    final_config = CONFIG.copy()
    final_config['best_val_accuracy'] = best_val_acc
    final_config['training_time_minutes'] = training_time / 60
    final_config['epochs_trained'] = epoch
    final_config['class_to_idx'] = class_to_idx
    
    with open(config_file, 'w') as f:
        json.dump(final_config, f, indent=2)
    
    logger.info(f"Configuration saved: {config_file}")
    
    print("\nNext step: Evaluate model")
    print("  python evaluate.py")


if __name__ == "__main__":
    main()
