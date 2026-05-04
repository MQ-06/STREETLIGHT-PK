import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent))

try:
    from utils.layer_orchestrator import LayerOrchestrator
    import torch
    
    print(f"PyTorch version: {torch.__version__}")
    
    # Attempt to initialize
    orchestrator = LayerOrchestrator()
    if orchestrator.layer1_available:
        print("SUCCESS: Layer 1 is available!")
    else:
        print("FAILURE: Layer 1 is in fallback mode.")
except Exception as e:
    import traceback
    traceback.print_exc()
