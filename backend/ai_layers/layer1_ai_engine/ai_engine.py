"""
AI Engine for StreetLight Image Classification
Main inference engine with prediction, severity estimation, and image hashing.
"""

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
import cv2
# import hashlib  # COMMENTED OUT - hash/duplicate detection will be added later
from pathlib import Path
from typing import Dict, List, Union, Optional
import logging

from ai_layers.layer1_ai_engine.model_loader import ModelLoader
from ai_layers.layer1_ai_engine.landmark_detector.verifier import GPSVerifier

logger = logging.getLogger(__name__)

# ImageNet normalization (same as training)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
IMAGE_SIZE = 224


class AIEngine:
    """
    AI Engine for image classification and analysis.
    
    Provides:
    - Image classification (pothole/garbage/other)
    - Confidence scoring
    - Severity estimation (small/medium/large)
    - Image hash calculation
    """
    
    def __init__(self, model_path: Path, confidence_threshold: float = 0.5):
        """
        Initialize AI Engine.
        
        Args:
            model_path: Path to trained model checkpoint
            confidence_threshold: Minimum confidence for valid predictions
        """
        self.confidence_threshold = confidence_threshold
        
        # Load model
        self.model_loader = ModelLoader(model_path)
        self.model = self.model_loader.get_model()
        self.device = self.model_loader.device
        self.class_names = self.model_loader.get_class_names()
        
        # Create transforms (same as validation)
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
        
        # Initialize GPS verifier for landmark detection
        self.gps_verifier = GPSVerifier()
        
        logger.info("✓ AI Engine initialized")
    
    def predict(
        self,
        image_path: Union[str, Path],
        submitted_lat: Optional[float] = None,
        submitted_lon: Optional[float] = None
    ) -> Dict:
        """
        Predict class of input image with GPS verification.
        
        Args:
            image_path: Path to image file
            submitted_lat: User-submitted latitude (optional)
            submitted_lon: User-submitted longitude (optional)
            
        Returns:
            Dictionary containing prediction results and GPS verification
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            # Load image
            image_pil = Image.open(image_path).convert('RGB')
            image_np = np.array(image_pil)
            
            # Preprocess for model
            image_tensor = self.transform(image_pil).unsqueeze(0).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = F.softmax(outputs, dim=1)[0]
            
            # Get prediction
            confidence, pred_idx = torch.max(probabilities, dim=0)
            confidence_value = confidence.item()
            predicted_class = self.class_names[pred_idx.item()]
            
            # Get all probabilities
            all_probs = {
                self.class_names[i]: float(probabilities[i].item() * 100)
                for i in range(len(self.class_names))
            }
            
            # Check if valid issue (not "other" class and above threshold)
            is_valid_issue = (
                predicted_class != "other" and
                confidence_value >= self.confidence_threshold
            )
            
            # Estimate severity if valid issue
            severity = None
            if is_valid_issue:
                severity = self._estimate_severity(image_np, predicted_class)
            
            # Calculate image hash (COMMENTED OUT -  add duplicate detection later)
            # image_hash = self._calculate_hash(image_path)
            image_hash = None
            
            # GPS Verification (landmark detection)
            logger.info("Running GPS verification...")
            gps_verification = self.gps_verifier.verify_location(
                image_path=image_path,
                submitted_lat=submitted_lat,
                submitted_lon=submitted_lon
            )
            
            # Calculate final score (AI confidence + GPS adjustment)
            ai_score = round(confidence_value * 100, 2)
            score_adjustment = gps_verification.get('score_adjustment', 0)
            final_score = max(0, min(100, ai_score + score_adjustment))
            
            # Generate user message (includes GPS info if relevant)
            message = self._generate_message(
                predicted_class,
                confidence_value,
                is_valid_issue,
                gps_verification
            )
            
            # Build result
            result = {
                'predicted_class': predicted_class,
                'confidence': round(confidence_value * 100, 2),
                'ai_score': ai_score,
                'severity': severity,
                'all_probabilities': {
                    k: round(v, 2) for k, v in all_probs.items()
                },
                'image_hash': image_hash,
                'is_valid_issue': is_valid_issue,
                'gps_verification': {
                    'has_photo_gps': gps_verification.get('has_photo_gps', False),
                    'photo_gps': gps_verification.get('photo_gps'),
                    'submitted_gps': gps_verification.get('submitted_gps'),
                    'photo_address': gps_verification.get('photo_address'),
                    'submitted_address': gps_verification.get('submitted_address'),
                    'distance_km': gps_verification.get('distance_km'),
                    'nearby_landmarks': gps_verification.get('nearby_landmarks', []),
                    'is_spoofed': gps_verification.get('is_spoofed', False),
                    'score_adjustment': score_adjustment,
                    'verification_status': gps_verification.get('verification_status', 'unknown'),
                    'penalty_reason': gps_verification.get('penalty_reason', '')
                },
                'final_score': round(final_score, 2),
                'message': message
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def predict_batch(self, image_paths: List[Union[str, Path]]) -> List[Dict]:
        """
        Predict classes for multiple images.
        
        Args:
            image_paths: List of image paths
            
        Returns:
            List of prediction dictionaries
        """
        results = []
        
        for img_path in image_paths:
            try:
                result = self.predict(img_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {img_path}: {str(e)}")
                results.append({
                    'error': str(e),
                    'image_path': str(img_path)
                })
        
        return results
    
    def _estimate_severity(self, image: np.ndarray, issue_type: str) -> str:
        """
        Estimate severity using COMBINED approach:
        1. Size-based detection (primary method)
        2. Feature-based detection (secondary/validation)
        
        Args:
            image: Image array (RGB)
            issue_type: Type of issue ('pothole' or 'garbage')
            
        Returns:
            Severity level: 'small', 'medium', or 'large'
        """
        try:
            # Method 1: Size-based detection (PRIMARY)
            size_severity = self._estimate_severity_by_size(image, issue_type)
            
            # Method 2: Feature-based detection (VALIDATION)
            feature_severity = self._estimate_severity_by_features(image, issue_type)
            
            # Combine both methods: take more severe result (conservative approach)
            severity_levels = {"small": 0, "medium": 1, "large": 2}
            
            size_level = severity_levels[size_severity]
            feature_level = severity_levels[feature_severity]
            
            # Take the higher severity (more conservative)
            final_level = max(size_level, feature_level)
            
            # Convert back to string
            for severity, level in severity_levels.items():
                if level == final_level:
                    logger.info(f"Severity: {severity} (size: {size_severity}, features: {feature_severity})")
                    return severity
            
            return "medium"  # Default fallback
            
        except Exception as e:
            logger.error(f"Severity estimation error: {str(e)}")
            return "medium"  # Default to medium if error
    
    def _estimate_severity_by_size(self, image: np.ndarray, issue_type: str) -> str:
        """
        Estimate severity based on physical size/dimensions of the issue.
        Uses contour detection to measure area coverage.
        
        Args:
            image: Image array (RGB)
            issue_type: Type of issue ('pothole' or 'garbage')
            
        Returns:
            Severity level: 'small', 'medium', or 'large'
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Resize for consistent processing
            gray = cv2.resize(gray, (224, 224))
            
            # Apply adaptive thresholding to find the issue region
            if issue_type == "pothole":
                # For potholes: threshold dark regions
                _, binary = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
            else:  # garbage
                # For garbage: use Otsu's method for adaptive thresholding
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find contours (outlines of the issue)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return "small"  # No clear issue detected
            
            # Get the largest contour (main issue)
            largest_contour = max(contours, key=cv2.contourArea)
            issue_area = cv2.contourArea(largest_contour)
            
            # Get bounding box dimensions
            x, y, w, h = cv2.boundingRect(largest_contour)
            bounding_box_area = w * h
            
            # Calculate coverage ratios
            image_area = gray.shape[0] * gray.shape[1]
            coverage_ratio = issue_area / image_area
            bbox_coverage = bounding_box_area / image_area
            
            # Use both actual area and bounding box for better estimation
            avg_coverage = (coverage_ratio + bbox_coverage) / 2
            
            # Classify based on coverage (adjusted thresholds for better accuracy)
            if issue_type == "pothole":
                # Potholes: More strict thresholds
                if avg_coverage > 0.25 or w > 150 or h > 150:  # >25% or large dimensions
                    return "large"
                elif avg_coverage > 0.12 or w > 80 or h > 80:  # 12-25% or medium dimensions
                    return "medium"
                else:
                    return "small"
            else:  # garbage
                # Garbage: Slightly looser thresholds (can be scattered)
                if avg_coverage > 0.30 or bbox_coverage > 0.40:  # >30% or large bounding box
                    return "large"
                elif avg_coverage > 0.15 or bbox_coverage > 0.20:  # 15-30%
                    return "medium"
                else:
                    return "small"
                    
        except Exception as e:
            logger.error(f"Size-based severity estimation error: {str(e)}")
            return "medium"
    
    def _estimate_severity_by_features(self, image: np.ndarray, issue_type: str) -> str:
        """
        Estimate severity using feature-based heuristics (ORIGINAL METHOD).
        Used as validation/backup for size-based method.
        
        For potholes: Based on dark pixel ratio and edge density
        For garbage: Based on texture complexity and area coverage
        
        Args:
            image: Image array (RGB)
            issue_type: Type of issue ('pothole' or 'garbage')
            
        Returns:
            Severity level: 'small', 'medium', or 'large'
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Resize for consistent processing
            gray = cv2.resize(gray, (224, 224))
            
            if issue_type == "pothole":
                # Pothole severity based on dark regions and edges
                
                # Calculate dark pixel ratio (potholes are typically dark)
                dark_threshold = 80
                dark_pixels = np.sum(gray < dark_threshold)
                dark_ratio = dark_pixels / gray.size
                
                # Calculate edge density (potholes have strong edges)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                
                # Combined severity score
                severity_score = (dark_ratio * 0.6 + edge_density * 0.4) * 100
                
                # Classify severity
                if severity_score > 15:
                    return "large"
                elif severity_score > 7:
                    return "medium"
                else:
                    return "small"
            
            elif issue_type == "garbage":
                # Garbage severity based on texture and coverage
                
                # Calculate texture complexity (garbage has high texture variance)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                texture_variance = laplacian.var()
                
                # Calculate coverage using thresholding
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                coverage = np.sum(binary < 128) / binary.size
                
                # Combined severity score
                severity_score = (texture_variance / 100 * 0.5 + coverage * 0.5) * 100
                
                # Classify severity
                if severity_score > 20:
                    return "large"
                elif severity_score > 10:
                    return "medium"
                else:
                    return "small"
            
            else:
                return "medium"
                
        except Exception as e:
            logger.error(f"Feature-based severity estimation error: {str(e)}")
            return "medium"  # Default to medium if error
    
    # DUPLICATE DETECTION - COMMENTED OUT (will be added in Layer 2)
    # def _calculate_hash(self, image_path: Path) -> str:
    #     """
    #     Calculate SHA-256 hash of image file.
    #     
    #     Args:
    #         image_path: Path to image file
    #         
    #     Returns:
    #         Hexadecimal hash string
    #     """
    #     try:
    #         sha256_hash = hashlib.sha256()
    #         
    #         with open(image_path, "rb") as f:
    #             # Read in chunks for large files
    #             for byte_block in iter(lambda: f.read(4096), b""):
    #                 sha256_hash.update(byte_block)
    #         
    #         return sha256_hash.hexdigest()
    #         
    #     except Exception as e:
    #         logger.error(f"Hash calculation error: {str(e)}")
    #         return "hash_unavailable"
    
    def _generate_message(
        self,
        predicted_class: str,
        confidence: float,
        is_valid: bool,
        gps_verification: Dict
    ) -> str:
        """
        Generate user-friendly message based on prediction and GPS verification.
        
        Args:
            predicted_class: Predicted class name
            confidence: Confidence score (0-1)
            is_valid: Whether it's a valid civic issue
            gps_verification: GPS verification results
            
        Returns:
            User-friendly message
        """
        confidence_pct = confidence * 100
        
        # Check for GPS spoofing first
        if gps_verification.get('is_spoofed', False):
            return (f"⚠️ GPS SPOOFING DETECTED: The photo's location differs from your "
                   f"submitted location by {gps_verification.get('distance_km', 0):.2f} km. "
                   f"Please ensure you're submitting accurate coordinates. "
                   f"Penalty applied: {gps_verification.get('score_adjustment', 0)} points.")
        
        if not is_valid:
            if predicted_class == "other":
                return ("This doesn't appear to be a civic issue (pothole or garbage). "
                       "Please upload a clear photo of a pothole or garbage pile.")
            else:
                return (f"Low confidence detection ({confidence_pct:.1f}%). "
                       f"The {predicted_class} is not clearly visible. "
                       "Please try taking the photo again from a different angle "
                       "with better lighting.")
        
        # Valid issue detected
        if confidence_pct >= 90:
            quality = "Clear"
        elif confidence_pct >= 70:
            quality = "Good"
        else:
            quality = "Acceptable"
        
        base_message = f"{quality} {predicted_class} detected with {confidence_pct:.1f}% confidence."
        
        # Add GPS verification status
        if gps_verification.get('verification_status') == 'verified':
            base_message += f" ✓ Location verified with nearby landmarks."
        elif gps_verification.get('verification_status') == 'good_match':
            base_message += f" ✓ Location matches submitted coordinates."
        elif gps_verification.get('verification_status') == 'minor_mismatch':
            base_message += (f" ⚠️ Minor location mismatch "
                           f"({gps_verification.get('distance_km', 0):.2f} km).")
        
        return base_message
    
    def get_model_info(self) -> Dict:
        """
        Get information about loaded model.
        
        Returns:
            Dictionary containing model metadata
        """
        return self.model_loader.get_metadata()
