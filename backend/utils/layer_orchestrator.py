"""
Layer Orchestrator - Coordinates validation and AI processing
This is the core integration component that manages the multi-layer AI agent
"""
import copy
import logging
import os
from pathlib import Path
from typing import Dict, Optional

from ai_layers.layer0_validation.input_validator import InputValidator

logger = logging.getLogger(__name__)

# NOTE: Do not import AIEngine at module level — it pulls in PyTorch (~huge RAM).
# On Render free (512MB), set SKIP_LAYER1_MODEL=true and PyTorch never loads.


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
        self._use_remote_ai = False
        self._remote_inference_url = (os.getenv("AI_INFERENCE_URL") or "").strip().rstrip(
            "/"
        )
        self._remote_inference_token = (os.getenv("AI_INFERENCE_TOKEN") or "").strip()

        skip_layer1 = os.getenv("SKIP_LAYER1_MODEL", "").lower() in (
            "1", "true", "yes", "on",
        )

        if self._remote_inference_url and skip_layer1:
            self._use_remote_ai = True
            self.layer1_available = True
            logger.info(
                "Layer 1: using remote classifier at %s (no local PyTorch)",
                self._remote_inference_url,
            )
        elif skip_layer1:
            logger.warning(
                "SKIP_LAYER1_MODEL is set — PyTorch / Layer 1 not loaded "
                "(required on Render free ~512MB). "
                "Set AI_INFERENCE_URL for remote AI, else fallback / manual review."
            )
        else:
            # Supported model filenames — add more if teammate uses different name
            backend_root = Path(__file__).resolve().parent.parent
            layer1_root = backend_root / "ai_layers" / "layer1_ai_engine"
            model_dirs = [layer1_root / "model", layer1_root / "models"]

            possible_model_names = [
                "best_model.pth",
                "best.pth",
                "model.pth",
                "model_final.pth",
                "streetlight.pth",
            ]

            model_path = None
            for models_dir in model_dirs:
                if not models_dir.exists():
                    continue
                for name in possible_model_names:
                    candidate = models_dir / name
                    if candidate.exists():
                        model_path = candidate
                        logger.info(f"✓ Found model file: {name} in {models_dir.name}/")
                        break
                if model_path is not None:
                    break

            if model_path is None:
                model_path = layer1_root / "models" / "best_model.pth"
                logger.info(
                    "No local model file found in model/ or models/. "
                    "Attempting Hugging Face download to models/best_model.pth..."
                )
                logger.info("Searched for: " + ", ".join(possible_model_names))

            try:
                # Lazy import keeps PyTorch off the heap when SKIP_LAYER1_MODEL=true
                from ai_layers.layer1_ai_engine.ai_engine import AIEngine

                self.ai_engine = AIEngine(model_path, confidence_threshold=0.68)
                self.layer1_available = True
                logger.info("✓ Layer 1 (AI Engine) initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️  Layer 1 failed to load model: {e}")
                logger.warning("⚠️  Layer 1 DISABLED — server running in fallback mode")

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
                'agent_reason': 'Image quality validation failed',
                'error_code': 'VALIDATION_FAILED',
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
                    'fallback_mode': True,
                    'image_hash': None,
                    'gps_verification': {
                        'verification_status': 'no_gps_in_photo',
                        'has_photo_gps': False,
                        'distance_km': None,
                        'is_spoofed': False,
                    },
                },
                'final_score': 50.0,          # Score 50 → goes to REVIEW queue
                'agent_decision': 'REVIEW',
                'agent_reason': 'AI model unavailable — officer review required',
                'error_code': None,
            }

        logger.info("🧠 Layer 1: Running AI classification & GPS verification...")

        if self._use_remote_ai:
            from utils.remote_ai_client import fetch_remote_classification
            from utils.layer1_result_builder import build_layer1_from_remote_json

            remote = fetch_remote_classification(
                self._remote_inference_url,
                image_path,
                token=self._remote_inference_token or None,
            )
            threshold = float(os.getenv("LAYER1_CONFIDENCE_THRESHOLD", "0.68"))
            ai_result = build_layer1_from_remote_json(
                image_path,
                latitude,
                longitude,
                remote,
                confidence_threshold=threshold,
            )
        else:
            ai_result = self.ai_engine.predict(
                image_path=image_path,
                submitted_lat=latitude,
                submitted_lon=longitude,
            )

        logger.info("Layer 1 Result:")
        logger.info(f"  - Class      : {ai_result['predicted_class']}")
        logger.info(f"  - Confidence : {ai_result['confidence']:.2f}%")
        logger.info(f"  - Severity   : {ai_result['severity']}")
        logger.info(f"  - Final Score: {ai_result['final_score']:.2f}/100")

        # Valid civic classification failed — try soft accept for ambiguous "other"
        if not ai_result['is_valid_issue']:
            probs = ai_result.get('all_probabilities') or {}
            civic_sum = probs.get('pothole', 0) + probs.get('garbage', 0)
            ambiguous_eligible = (
                ai_result['predicted_class'] == 'other'
                and validation_result['overall_quality'] >= 48.0
                and civic_sum >= 8.0
            )
            if ambiguous_eligible:
                logger.warning(
                    "⚠️ AI AGENT: Ambiguous classification (other) — accepting for OFFICER REVIEW"
                )
                ai_accept = copy.deepcopy(ai_result)
                picked = (
                    'pothole' if probs.get('pothole', 0) >= probs.get('garbage', 0) else 'garbage'
                )
                runner_conf = max(probs.get('pothole', 0), probs.get('garbage', 0))
                ai_accept['predicted_class'] = picked
                ai_accept['is_valid_issue'] = True
                ai_accept['ambiguous_classification'] = True
                ai_accept['confidence'] = round(runner_conf, 2)
                ai_accept['severity'] = 'medium'
                ai_score = runner_conf
                score_adjustment = ai_accept['gps_verification'].get('score_adjustment', 0)
                severity_bonus = 0
                merged = max(0, min(100, ai_score + score_adjustment + severity_bonus))
                ai_accept['final_score'] = round(max(merged, 62.0), 2)
                ai_accept['message'] = (
                    'Submitted for staff review — the photo did not clearly match pothole or litter '
                    'automatically. City staff will confirm the issue type.'
                )
                ai_result = ai_accept
            else:
                logger.warning("❌ AI AGENT DECISION: REJECT — Not a valid civic issue")
                logger.info("=" * 60)

                err_code = (
                    'UNKNOWN_ISSUE_TYPE'
                    if ai_result['predicted_class'] == 'other'
                    else 'LOW_AI_CONFIDENCE'
                )
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
                    'agent_reason': 'AI confidence too low or not a civic issue',
                    'error_code': err_code,
                }

        # Enforce minimum final score threshold (hard reject below 60/100)
        if ai_result['final_score'] < 60.0:
            logger.warning(
                "❌ AI AGENT DECISION: REJECT — Final score below threshold "
                f"({ai_result['final_score']:.2f} < 60.00)"
            )
            logger.info("=" * 60)

            return {
                'passed': False,
                'errors': [
                    f"AI final confidence score too low ({ai_result['final_score']:.1f}/100). "
                    "Reports scoring below 60 are automatically rejected."
                ],
                'warnings': validation_result['warnings'],
                'layer0': validation_result,
                'layer1': ai_result,
                'final_score': ai_result['final_score'],
                'agent_decision': 'REJECTED',
                'agent_reason': 'AI final score below acceptance threshold (60/100)',
                'error_code': 'LOW_AI_SCORE',
            }

        # ==========================================
        # COMBINE RESULTS — ACCEPT (or REVIEW if ambiguous category)
        # ==========================================
        if ai_result.get('ambiguous_classification'):
            logger.info("✅ AI AGENT DECISION: ACCEPT — QUEUED FOR REVIEW (ambiguous type)")
        else:
            logger.info("✅ AI AGENT DECISION: ACCEPT")
        logger.info(f"   Final Score : {ai_result['final_score']:.2f}/100")
        logger.info(f"   Message     : {ai_result['message']}")
        logger.info("=" * 60)

        agent_decision = 'REVIEW' if ai_result.get('ambiguous_classification') else 'ACCEPTED'
        warnings_out = list(validation_result['warnings'])
        if ai_result.get('ambiguous_classification'):
            warnings_out.append(
                'Automatic category unclear — classified from weaker signals; officer review.'
            )

        return {
            'passed': True,
            'errors': [],
            'warnings': warnings_out,
            'layer0': validation_result,
            'layer1': ai_result,
            'final_score': ai_result['final_score'],
            'agent_decision': agent_decision,
            'agent_reason': ai_result['message'],
            'error_code': None,
        }

    def get_health_status(self) -> Dict:
        """
        Check if both layers are operational

        Returns:
            Health status of all AI components
        """
        if self._use_remote_ai:
            return {
                'status': 'healthy',
                'layer0_status': 'operational',
                'layer1_status': 'operational (remote)',
                'message': f'Remote classifier: {self._remote_inference_url}',
                'remote_url': self._remote_inference_url,
            }

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
