"""
Quick test — pass any image through the full AI pipeline.
Usage:
    python test_prediction.py <path_to_image>
    python test_prediction.py  (uses a sample from test set automatically)
"""

import sys
from pathlib import Path

# Add inference dir to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_engine import AIEngine

MODEL_PATH   = Path(__file__).parent.parent / "training" / "models" / "best_model.pth"
TEST_DATA    = Path(__file__).parent.parent / "training" / "data" / "test"

def find_sample_image():
    """Pick one image from each class in the test set."""
    samples = {}
    for cls in ["garbage", "pothole", "other"]:
        folder = TEST_DATA / cls
        if folder.exists():
            imgs = list(folder.glob("*.jpg"))[:1]
            if imgs:
                samples[cls] = imgs[0]
    return samples

def run_test(image_path: Path):
    print(f"\nImage : {image_path.name}")
    print("-" * 50)
    result = engine.predict(image_path)

    print(f"Predicted : {result['predicted_class'].upper()}")
    print(f"Confidence: {result['confidence']:.2f}%")
    print(f"Severity  : {result['severity'] or 'N/A (not a civic issue)'}")
    print(f"Valid Issue: {result['is_valid_issue']}")
    print(f"Final Score: {result['final_score']}")
    print(f"\nAll probabilities:")
    for cls, prob in sorted(result['all_probabilities'].items(), key=lambda x: -x[1]):
        bar = "█" * int(prob / 5)
        print(f"  {cls:<10} {prob:>6.2f}%  {bar}")
    print(f"\nMessage: {result['message']}")


# Load engine once
print("Loading AI Engine...")
engine = AIEngine(MODEL_PATH, confidence_threshold=0.70)
print("Ready.\n")

if len(sys.argv) > 1:
    # User passed an image path
    img = Path(sys.argv[1])
    if not img.exists():
        print(f"File not found: {img}")
        sys.exit(1)
    run_test(img)
else:
    # Auto-pick one sample from each test class
    samples = find_sample_image()
    if not samples:
        print("No test images found. Pass an image path as argument:")
        print("  python test_prediction.py path/to/image.jpg")
        sys.exit(1)

    print(f"Running on {len(samples)} sample images from test set...\n")
    for cls, img_path in samples.items():
        print(f"[Expected: {cls.upper()}]")
        run_test(img_path)
        print()
