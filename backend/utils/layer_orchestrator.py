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
        logger.info("=" * 60)
        logger.info("Initializing Layer Orchestrator (AI Agent)...")
        logger.info("=" * 60)

        # ==========================================
        # LAYER 0: INPUT VALIDATION
        # ==========================================
        logger.info("Loading Layer 0: Input Validation...")
        self.input_validator = InputValidator()
        logger.info("✓ Layer 0 (Input Validation) initialized")

        # ==========================================
        # LAYER 1: AI ENGINE (with graceful fallback)
        # ==========================================
        logger.info("Loading Layer 1: AI Classification Engine...")

        self.ai_engine = None
        self.layer1_available = False

        # Supported model filenames — add more if teammate uses different name
        backend_root = Path(__file__).resolve().parent.parent
        models_dir = backend_root / "ai_layers" / "layer1_ai_engine" / "model"

        possible_model_names = [
            "best_model.pth",   # original expected name
            "best.pth",         # teammate might use this
            "model.pth",
            "model_final.pth",
            "streetlight.pth",
        ]

        model_path = None
        for name in possible_model_names:
            candidate = models_dir / name
            if candidate.exists():
                model_path = candidate
                logger.info(f"✓ Found model file: {name}")
                break

        if model_path is not None:
            try:
                self.ai_engine = AIEngine(model_path, confidence_threshold=0.5)
                self.layer1_available = True
                logger.info("✓ Layer 1 (AI Engine) initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️  Layer 1 failed to load model: {e}")
                logger.warning("⚠️  Running in FALLBACK mode — AI scoring disabled")
        else:
            logger.warning(f"⚠️  No model file found in: {models_dir}")
            logger.warning("⚠️  Searched for: " + ", ".join(possible_model_names))
            logger.warning("⚠️  Layer 1 DISABLED — server running in fallback mode")
            logger.warning("⚠️  ACTION NEEDED: Get model file from your teammate!")

        logger.info("=" * 60)
        logger.info("✅ AI Agent Ready — Layer 1: {}".format(
            "Operational" if self.layer1_available else "FALLBACK MODE (manual review)"
        ))
        logger.info("=" * 60)

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
            latitude:   GPS latitude (required)
            longitude:  GPS longitude (required)

        Returns:
            Dictionary with processing results:
            {
                'passed': bool,              # True = Accept, False = Reject
                'errors': list,              # Reasons for rejection
                'warnings': list,            # Non-critical issues
                'layer0': {...},             # Validation results
                'layer1': {...},             # AI results (None if layer0 failed)
                'final_score': float,        # Combined score (0-100)
                'agent_decision': str,       # ACCEPTED / REVIEW / REJECTED
                'agent_reason': str          # Human-readable reason
            }
        """
        logger.info("=" * 60)
        logger.info("🤖 AI AGENT: Processing new report")
        logger.info(f"   Image : {Path(image_path).name}")
        logger.info(f"   GPS   : ({latitude}, {longitude})")
        logger.info("=" * 60)

        # ==========================================
        # LAYER 0: INPUT VALIDATION
        # ==========================================
        logger.info("🔍 Layer 0: Running input validation checks...")

        validation_result = self.input_validator.validate_all(
            image_path=image_path,
            latitude=latitude,
            longitude=longitude
        )

        logger.info(
            f"Layer 0 Result: valid={validation_result['is_valid']}, "
            f"quality={validation_result['overall_quality']:.2f}/100"
        )

        # If validation fails → reject immediately, no need to run AI
        if not validation_result['is_valid']:
            logger.warning("❌ AI AGENT DECISION: REJECT — Failed Layer 0 validation")
            logger.warning(f"   Reasons: {validation_result['errors']}")
            logger.info("=" * 60)

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

        logger.info("✓ Layer 0 passed — image quality acceptable")

        # ==========================================
        # LAYER 1: AI CLASSIFICATION + GPS
        # ==========================================

        # FALLBACK: Model not available → send to officer manual review
        if not self.layer1_available:
            logger.warning("⚠️  Layer 1 unavailable — applying fallback score (50/100)")
            logger.warning("⚠️  Report routed to officer manual review queue")
            logger.info("=" * 60)

            return {
                'passed': True,
                'errors': [],
                'warnings': validation_result['warnings'] + [
                    "AI model unavailable — report sent to officer manual review"
                ],
                'layer0': validation_result,
                'layer1': {
                    'predicted_class': 'unknown',
                    'confidence': 0.0,
                    'severity': 'unknown',
                    'final_score': 50.0,
                    'is_valid_issue': True,
                    'message': 'AI model not loaded — manual review required',
                    'fallback_mode': True
                },
                'final_score': 50.0,          # Score 50 → goes to REVIEW queue
                'agent_decision': 'REVIEW',
                'agent_reason': 'AI model unavailable — officer review required'
            }

        logger.info("🧠 Layer 1: Running AI classification & GPS verification...")

        ai_result = self.ai_engine.predict(
            image_path=image_path,
            submitted_lat=latitude,
            submitted_lon=longitude
        )

        logger.info("Layer 1 Result:")
        logger.info(f"  - Class      : {ai_result['predicted_class']}")
        logger.info(f"  - Confidence : {ai_result['confidence']:.2f}%")
        logger.info(f"  - Severity   : {ai_result['severity']}")
        logger.info(f"  - Final Score: {ai_result['final_score']:.2f}/100")

        # Check if it's a valid civic issue
        if not ai_result['is_valid_issue']:
            logger.warning("❌ AI AGENT DECISION: REJECT — Not a valid civic issue")
            logger.info("=" * 60)

            return {
                'passed': False,
                'errors': [
                    f"AI could not identify a valid civic issue. "
                    f"Detected: {ai_result['predicted_class']} "
                    f"with {ai_result['confidence']:.1f}% confidence."
                ],
                'warnings': validation_result['warnings'],
                'layer0': validation_result,
                'layer1': ai_result,
                'final_score': ai_result['final_score'],
                'agent_decision': 'REJECTED',
                'agent_reason': 'AI confidence too low or not a civic issue'
            }

        # ==========================================
        # COMBINE RESULTS — ACCEPT
        # ==========================================
        logger.info("✅ AI AGENT DECISION: ACCEPT")
        logger.info(f"   Final Score : {ai_result['final_score']:.2f}/100")
        logger.info(f"   Message     : {ai_result['message']}")
        logger.info("=" * 60)

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
        if not self.layer1_available:
            return {
                'status': 'degraded',
                'layer0_status': 'operational',
                'layer1_status': 'UNAVAILABLE — model file missing',
                'message': (
                    'Server running in fallback mode. '
                    'Place best_model.pth (or best.pth) in '
                    'ai_layers/layer1_ai_engine/models/ and restart.'
                )
            }

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
                'layer0_status': 'operational',
                'layer1_status': 'error',
                'error': str(e),
                'message': 'AI Agent experiencing issues'
            }
            
            
            
"""
            # PEHLE — crash karta tha:
raise FileNotFoundError(...)   # ← server band ho jata

# AB — gracefully handle karta hai:
if model_path exists → load karo, kaam karo normally
if model_path missing → warning log karo, fallback mode
```



## Jab Model File Milegi Tab Kya Hoga?
```
Step 1: Folder banao (agar nahi hai)
        backend/ai_layers/layer1_ai_engine/models/

Step 2: File daalo — koi bhi naam ho:
        best.pth        ✅ auto-detect
        best_model.pth  ✅ auto-detect
        model.pth       ✅ auto-detect

Step 3: Uvicorn auto-reload karta hai (--reload flag hai)

Step 4: AI Engine full power mein kaam karta hai
        Score 50 fallback → BAND
        Real AI scores → SHURU (0-100 proper)"""