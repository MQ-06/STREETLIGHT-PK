"""
Model Evaluation Script
Evaluates trained model and generates detailed metrics and visualizations.

Usage:
    python evaluate.py
"""

import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
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

# Paths
DATA_DIR = Path(__file__).parent / "data"
TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "val"
MODELS_DIR = Path(__file__).parent / "models"


def load_model(checkpoint_path: Path, device: torch.device) -> Tuple[nn.Module, Dict]:
    """
    Load trained model from checkpoint.
    
    Args:
        checkpoint_path: Path to checkpoint file
        device: Device to load model on
        
    Returns:
        Tuple of (model, checkpoint_info)
    """
    logger.info(f"Loading model from: {checkpoint_path}")
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Create model
    num_classes = checkpoint['config']['num_classes']
    model = models.resnet18(pretrained=False)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    
    # Load weights
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    logger.info(f"✓ Model loaded successfully")
    logger.info(f"  Trained for {checkpoint['epoch']} epochs")
    logger.info(f"  Best val accuracy: {checkpoint['val_accuracy']:.2f}%")
    
    return model, checkpoint


def evaluate_model(
    model: nn.Module,
    data_loader: torch.utils.data.DataLoader,
    device: torch.device
) -> Tuple[List[int], List[int], List[float]]:
    """
    Evaluate model and collect predictions.
    
    Args:
        model: PyTorch model
        data_loader: Data loader
        device: Device
        
    Returns:
        Tuple of (true_labels, predicted_labels, confidences)
    """
    model.eval()
    
    all_labels = []
    all_predictions = []
    all_confidences = []
    
    logger.info("Evaluating model on validation set...")
    
    with torch.no_grad():
        for inputs, labels in tqdm(data_loader, desc="Evaluating"):
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Forward pass
            outputs = model(inputs)
            probabilities = torch.softmax(outputs, dim=1)
            confidences, predictions = torch.max(probabilities, dim=1)
            
            # Collect results
            all_labels.extend(labels.cpu().numpy())
            all_predictions.extend(predictions.cpu().numpy())
            all_confidences.extend(confidences.cpu().numpy())
    
    return all_labels, all_predictions, all_confidences


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str],
    save_path: Path
):
    """
    Plot and save confusion matrix.
    
    Args:
        cm: Confusion matrix
        class_names: List of class names
        save_path: Path to save plot
    """
    plt.figure(figsize=(10, 8))
    
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=class_names,
        yticklabels=class_names,
        cbar=True
    )
    
    plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Confusion matrix saved: {save_path}")
    plt.close()


def plot_training_history(history_path: Path, save_path: Path):
    """
    Plot training and validation metrics over epochs.
    
    Args:
        history_path: Path to training history JSON
        save_path: Path to save plot
    """
    with open(history_path, 'r') as f:
        history = json.load(f)
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    epochs = range(1, len(history['train_loss']) + 1)
    
    # Loss plot
    axes[0].plot(epochs, history['train_loss'], 'b-', label='Train Loss', linewidth=2)
    axes[0].plot(epochs, history['val_loss'], 'r-', label='Val Loss', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Accuracy plot
    axes[1].plot(epochs, history['train_acc'], 'b-', label='Train Accuracy', linewidth=2)
    axes[1].plot(epochs, history['val_acc'], 'r-', label='Val Accuracy', linewidth=2)
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Accuracy (%)', fontsize=12)
    axes[1].set_title('Training and Validation Accuracy', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Training history plot saved: {save_path}")
    plt.close()


def calculate_metrics(
    true_labels: List[int],
    predicted_labels: List[int],
    class_names: List[str]
) -> Dict:
    """
    Calculate detailed evaluation metrics.
    
    Args:
        true_labels: Ground truth labels
        predicted_labels: Predicted labels
        class_names: List of class names
        
    Returns:
        Dictionary containing all metrics
    """
    # Confusion matrix
    cm = confusion_matrix(true_labels, predicted_labels)
    
    # Classification report
    report = classification_report(
        true_labels,
        predicted_labels,
        target_names=class_names,
        output_dict=True
    )
    
    # Overall accuracy
    accuracy = (np.array(predicted_labels) == np.array(true_labels)).mean() * 100
    
    # Per-class accuracy
    per_class_acc = {}
    for i, class_name in enumerate(class_names):
        mask = np.array(true_labels) == i
        if mask.sum() > 0:
            class_correct = (np.array(predicted_labels)[mask] == i).sum()
            per_class_acc[class_name] = (class_correct / mask.sum()) * 100
        else:
            per_class_acc[class_name] = 0.0
    
    metrics = {
        'overall_accuracy': accuracy,
        'per_class_accuracy': per_class_acc,
        'confusion_matrix': cm.tolist(),
        'classification_report': report
    }
    
    return metrics


def print_evaluation_report(metrics: Dict, class_names: List[str]):
    """
    Print formatted evaluation report.
    
    Args:
        metrics: Metrics dictionary
        class_names: List of class names
    """
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)
    
    print(f"\nOverall Accuracy: {metrics['overall_accuracy']:.2f}%")
    
    print("\n" + "-"*80)
    print("Per-Class Accuracy:")
    print("-"*80)
    for class_name in class_names:
        acc = metrics['per_class_accuracy'][class_name]
        print(f"  {class_name:<15} {acc:>6.2f}%")
    
    print("\n" + "-"*80)
    print("Detailed Classification Report:")
    print("-"*80)
    
    report = metrics['classification_report']
    
    print(f"\n{'Class':<15} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}")
    print("-"*80)
    
    for class_name in class_names:
        class_report = report[class_name]
        print(f"{class_name:<15} "
              f"{class_report['precision']:>10.4f} "
              f"{class_report['recall']:>10.4f} "
              f"{class_report['f1-score']:>10.4f} "
              f"{int(class_report['support']):>10}")
    
    # Macro and weighted averages
    print("-"*80)
    macro_avg = report['macro avg']
    weighted_avg = report['weighted avg']
    
    print(f"{'Macro Avg':<15} "
          f"{macro_avg['precision']:>10.4f} "
          f"{macro_avg['recall']:>10.4f} "
          f"{macro_avg['f1-score']:>10.4f}")
    
    print(f"{'Weighted Avg':<15} "
          f"{weighted_avg['precision']:>10.4f} "
          f"{weighted_avg['recall']:>10.4f} "
          f"{weighted_avg['f1-score']:>10.4f}")
    
    print("="*80)


def main():
    """Main evaluation function."""
    
    print("="*80)
    print("StreetLight AI Engine - Model Evaluation")
    print("="*80)
    print()
    
    # Check if model exists
    model_path = MODELS_DIR / "best_model.pth"
    if not model_path.exists():
        logger.error(f"Model not found: {model_path}")
        logger.error("\nPlease train model first:")
        logger.error("  python train.py")
        return
    
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    
    # Load model
    model, checkpoint = load_model(model_path, device)
    
    # Get class names
    idx_to_class = checkpoint['idx_to_class']
    # Handle both string and integer keys
    class_names = []
    for i in range(len(idx_to_class)):
        # Try integer key first, then string key
        if i in idx_to_class:
            class_names.append(idx_to_class[i])
        elif str(i) in idx_to_class:
            class_names.append(idx_to_class[str(i)])
    logger.info(f"Classes: {class_names}")
    
    # Load data
    logger.info("\nLoading validation data...")
    _, val_loader, _ = get_data_loaders(
        train_dir=TRAIN_DIR,
        val_dir=VAL_DIR,
        batch_size=32,
        num_workers=4
    )
    
    # Evaluate model
    true_labels, predicted_labels, confidences = evaluate_model(
        model, val_loader, device
    )
    
    # Calculate metrics
    logger.info("\nCalculating metrics...")
    metrics = calculate_metrics(true_labels, predicted_labels, class_names)
    
    # Print report
    print_evaluation_report(metrics, class_names)
    
    # Save metrics
    metrics_file = MODELS_DIR / "evaluation_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"\n✓ Metrics saved: {metrics_file}")
    
    # Plot confusion matrix
    cm = np.array(metrics['confusion_matrix'])
    plot_confusion_matrix(
        cm,
        class_names,
        MODELS_DIR / "confusion_matrix.png"
    )
    
    # Plot training history
    history_path = MODELS_DIR / "training_history.json"
    if history_path.exists():
        plot_training_history(
            history_path,
            MODELS_DIR / "training_history.png"
        )
    
    # Success message
    print("\n" + "="*80)
    print("Evaluation Complete!")
    print("="*80)
    print(f"\nGenerated files:")
    print(f"  - {MODELS_DIR / 'evaluation_metrics.json'}")
    print(f"  - {MODELS_DIR / 'confusion_matrix.png'}")
    print(f"  - {MODELS_DIR / 'training_history.png'}")
    print()
    
    # Performance assessment
    accuracy = metrics['overall_accuracy']
    if accuracy >= 90:
        print(f"✓ Excellent performance! ({accuracy:.2f}% accuracy)")
    elif accuracy >= 85:
        print(f"✓ Good performance! ({accuracy:.2f}% accuracy)")
    elif accuracy >= 75:
        print(f"⚠ Acceptable performance ({accuracy:.2f}% accuracy)")
        print("  Consider collecting more training data or adjusting hyperparameters.")
    else:
        print(f"✗ Low performance ({accuracy:.2f}% accuracy)")
        print("  Recommendations:")
        print("  - Collect more training data (aim for 200+ images per class)")
        print("  - Check data quality (blurry/corrupted images)")
        print("  - Balance class distribution")
        print("  - Increase training epochs")


if __name__ == "__main__":
    main()

