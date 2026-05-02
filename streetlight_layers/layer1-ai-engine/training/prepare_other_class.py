"""
Copy a random balanced sample from raw_images/other/ into pakistani_dataset/other/.

We have 15,273 existing "other" images — already diverse (buildings, nature,
people, food, streets). We just copy 900 of them. No augmentation needed
because diversity comes from sampling 900 different images, not repeating
the same image with transforms.

Target: ~900 images (matches the 860 clean garbage images we have)

Run:
    python prepare_other_class.py
"""

import random
import shutil
from pathlib import Path

import cv2
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SOURCE_DIR = (
    Path(__file__).parent / "data" / "raw_images" / "other"
)
OUTPUT_DIR = (
    Path(__file__).parent / "data" / "pakistani_dataset" / "other"
)

TARGET_COUNT = 900   # how many to copy — matches garbage class size
SEED         = 42
MIN_DIM      = 100   # px — skip any corrupted tiny files


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def prepare():
    random.seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all source images
    exts    = {".jpg", ".jpeg", ".png"}
    sources = [p for p in SOURCE_DIR.iterdir() if p.suffix.lower() in exts]

    if not sources:
        print(f"No images found in {SOURCE_DIR}")
        return

    print(f"Source images available : {len(sources)}")
    print(f"Target to copy          : {TARGET_COUNT}")
    print(f"Output folder           : {OUTPUT_DIR}")
    print()

    # Shuffle and pick TARGET_COUNT
    random.shuffle(sources)
    candidates = sources[:TARGET_COUNT * 2]   # take 2x to account for bad ones

    copied   = 0
    skipped  = 0

    for src in tqdm(candidates, desc="Copying", unit="img"):
        if copied >= TARGET_COUNT:
            break

        # Quick sanity check — skip unreadable or tiny images
        img = cv2.imread(str(src))
        if img is None:
            skipped += 1
            continue
        h, w = img.shape[:2]
        if w < MIN_DIM or h < MIN_DIM:
            skipped += 1
            continue

        dest_name = f"other_{copied + 1:04d}{src.suffix.lower()}"
        shutil.copy2(str(src), str(OUTPUT_DIR / dest_name))
        copied += 1

    print()
    print("=" * 55)
    print("PREPARE OTHER CLASS COMPLETE")
    print("=" * 55)
    print(f"  Copied   : {copied}")
    print(f"  Skipped  : {skipped}  (unreadable or too small)")
    print(f"  Output   : {OUTPUT_DIR}")
    print("=" * 55)
    print()
    print("Dataset class balance so far:")
    garbage_aug = Path(__file__).parent / "data" / "pakistani_dataset" / "garbage_augmented"
    garbage_count = len(list(garbage_aug.glob("*.jpg"))) if garbage_aug.exists() else 0
    print(f"  garbage_augmented/ : {garbage_count} images")
    print(f"  other/             : {copied} images")
    print(f"  pothole/           : 0 images  (Priority #6 — next)")
    print()
    print("NEXT STEPS:")
    print("  1. Run CLIP filter to remove any garbage-like images from other/:")
    print("     python clip_filter_other.py")
    print("  2. Then proceed to pothole class (Priority #6)")
    print("  3. Then retrain:  python train.py  (Priority #5)")


if __name__ == "__main__":
    prepare()
