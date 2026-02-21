"""
Layer Orchestrator - Coordinates validation and AI processing
This is the core integration component that manages the multi-layer AI agent
"""
import logging
from pathlib import Path
from typing import Dict, Optional

from ai_layers.layer0_validation.input_validator import InputValidator
from ai_layers.layer1_ai_engine.ai_engine import AIEngine

logger = logging.getLogger(__name__)


class LayerOrchestrator:
    """
    Orchestrates image processing through validation and AI layers
    
    This class acts as the AI agent's coordinator, running reports through:
    1. Layer 0: Input validation (quality checks)
    2. Layer 1: AI classification + GPS verification
    
    The agent automatically accepts or rejects reports based on the results.
    """
    
    def __init__(self):
        """Initialize both validation layers"""
        logger.info("="*60)
        logger.info("Initializing Layer Orchestrator (AI Agent)...")
        logger.info("="*60)
        
        # Layer 0: Input Validation
        logger.info("Loading Layer 0: Input Validation...")
        self.input_validator = InputValidator()
        logger.info("✓ Layer 0 (Input Validation) initialized")
        
        # Layer 1: AI Engine
        logger.info("Loading Layer 1: AI Classification Engine...")
        model_path = Path(__file__).parent.parent / "ai_layers" / "layer1_ai_engine" / "models" / "best_model.pth"
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"AI model not found at {model_path}. "
                f"Please ensure best_model.pth is copied to ai_layers/layer1_ai_engine/models/"
            )
        
        self.ai_engine = AIEngine(model_path, confidence_threshold=0.5)
        logger.info("✓ Layer 1 (AI Engine) initialized")
        logger.info("="*60)
        logger.info("✅ AI Agent Ready - All Layers Operational")
        logger.info("="*60)
    
    def process_report(
        self,
        image_path: str,
        latitude: Optional[float],
        longitude: Optional[float]
    ) -> Dict:
        """
        Process a report through all validation layers (AI Agent workflow)
        
        The AI agent automatically:
        1. Validates image quality (blur, brightness, resolution, etc.)
        2. Classifies the issue using deep learning (pothole/garbage)
        3. Estimates severity (small/medium/large)
        4. Verifies GPS location (detects spoofing)
        5. Returns accept/reject decision with reasoning
        
        Args:
            image_path: Path to temporary image file
            latitude: GPS latitude (required)
            longitude: GPS longitude (required)
            
        Returns:
            Dictionary with processing results:
            {
                'passed': bool,              # True = Accept, False = Reject
                'errors': list,              # Reasons for rejection
                'warnings': list,            # Non-critical issues
                'layer0': {...},             # Validation results
                'layer1': {...},             # AI results (only if layer0 passed)
                'final_score': float         # Combined score (0-100)
            }
        """
        logger.info("="*60)
        logger.info(f"🤖 AI AGENT: Processing new report")
        logger.info(f"Image: {Path(image_path).name}")
        logger.info(f"GPS: ({latitude}, {longitude})")
        logger.info("="*60)
        
        # ==========================================
        # LAYER 0: INPUT VALIDATION
        # ==========================================
        logger.info("🔍 Layer 0: Running input validation checks...")
        
        validation_result = self.input_validator.validate_all(
            image_path=image_path,
            latitude=latitude,
            longitude=longitude
        )
        
        logger.info(f"Layer 0 Result: valid={validation_result['is_valid']}, "
                   f"quality={validation_result['overall_quality']:.2f}/100")
        
        # If validation fails, stop here and reject
        if not validation_result['is_valid']:
            logger.warning("❌ AI AGENT DECISION: REJECT - Failed Layer 0 validation")
            logger.warning(f"Rejection reasons: {validation_result['errors']}")
            logger.info("="*60)
            
            return {
                'passed': False,
                'errors': validation_result['errors'],
                'warnings': validation_result['warnings'],
                'layer0': validation_result,
                'layer1': None,
                'final_score': 0.0,
                'agent_decision': 'REJECTED',
                'agent_reason': 'Image quality validation failed'
            }
        
        logger.info("✓ Layer 0 passed - Image quality acceptable")
        
        # ==========================================
        # LAYER 1: AI CLASSIFICATION + GPS
        # ==========================================
        logger.info("🧠 Layer 1: Running AI classification & GPS verification...")
        
        ai_result = self.ai_engine.predict(
            image_path=image_path,
            submitted_lat=latitude,
            submitted_lon=longitude
        )
        
        logger.info(f"Layer 1 Result:")
        logger.info(f"  - Class: {ai_result['predicted_class']}")
        logger.info(f"  - Confidence: {ai_result['confidence']:.2f}%")
        logger.info(f"  - Severity: {ai_result['severity']}")
        logger.info(f"  - Final Score: {ai_result['final_score']:.2f}/100")
        
        # Check if it's a valid civic issue
        if not ai_result['is_valid_issue']:
            logger.warning("❌ AI AGENT DECISION: REJECT - Not a valid civic issue")
            logger.info("="*60)
            
            return {
                'passed': False,
                'errors': [
                    f"AI could not identify a valid civic issue. "
                    f"Detected: {ai_result['predicted_class']} with {ai_result['confidence']:.1f}% confidence."
                ],
                'warnings': validation_result['warnings'],
                'layer0': validation_result,
                'layer1': ai_result,
                'final_score': ai_result['final_score'],
                'agent_decision': 'REJECTED',
                'agent_reason': 'AI confidence too low or not a civic issue'
            }
        
        # ==========================================
        # COMBINE RESULTS - ACCEPT
        # ==========================================
        logger.info("✅ AI AGENT DECISION: ACCEPT")
        logger.info(f"Final Score: {ai_result['final_score']:.2f}/100")
        logger.info(f"Message: {ai_result['message']}")
        logger.info("="*60)
        
        return {
            'passed': True,
            'errors': [],
            'warnings': validation_result['warnings'],
            'layer0': validation_result,
            'layer1': ai_result,
            'final_score': ai_result['final_score'],
            'agent_decision': 'ACCEPTED',
            'agent_reason': ai_result['message']
        }
    
    def get_health_status(self) -> Dict:
        """
        Check if both layers are operational
        
        Returns:
            Health status of all AI components
        """
        try:
            model_info = self.ai_engine.get_model_info()
            
            return {
                'status': 'healthy',
                'layer0_status': 'operational',
                'layer1_status': 'operational',
                'model_info': model_info,
                'message': 'AI Agent fully operational'
            }
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e),
                'message': 'AI Agent experiencing issues'
            }

