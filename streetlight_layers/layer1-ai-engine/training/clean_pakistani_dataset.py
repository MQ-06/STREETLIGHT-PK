"""
Auto-clean a Pakistani garbage image folder.

Usage:
    python clean_pakistani_dataset.py                         # cleans garbage/
    python clean_pakistani_dataset.py garbage_augmented       # cleans garbage_augmented/

Moves bad images to:  <source_folder>_rejected/
Does NOT delete anything — verify the rejects before removing.

Bad image categories detected:
  1. Infographics / colored-dot charts  — too many highly-saturated pixels
  2. Near-blank / uniform images        — pixel variance too low
  3. Unusably blurry                    — Laplacian variance too low
  4. Too small                          — dimensions under 300×300

Run:
    pip install opencv-python pillow tqdm numpy
    python clean_pakistani_dataset.py garbage_augmented
"""

import sys
import shutil
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent / "data" / "pakistani_dataset"

# Accept folder name as optional CLI argument; default to "garbage"
_folder_arg  = sys.argv[1] if len(sys.argv) > 1 else "garbage"
SOURCE_DIR   = BASE_DIR / _folder_arg
REJECTED_DIR = BASE_DIR / f"{_folder_arg}_rejected"

# Thresholds — tuned for real street photography vs infographics
MIN_DIMENSION       = 100      # px — reject if width OR height below this
# Note: augmented images are intentionally 224×224 (ResNet input size) so
# the old 300px threshold wrongly rejected all of them. 100px catches only
# truly broken thumbnails while keeping valid 224×224 augmented images.

# Infographic / colored-dot detection:
# In HSV, saturation 0-255. Pure infographic colors (red/blue/green dots)
# have saturation > 180. Real street photos rarely exceed 15% such pixels.
SATURATION_THRESHOLD   = 180   # HSV saturation value considered "too pure"
MAX_SATURATED_RATIO    = 0.15  # if >15% of pixels are this saturated → reject

# Blank image detection:
# Standard deviation of grayscale pixel values. A near-white or near-black
# image has very low std. Real photos are typically > 20.
MIN_PIXEL_STD = 18.0

# Blur detection:
# Laplacian variance measures edge sharpness. Very blurry images (motion
# blur so extreme the image is unrecognisable) score < 30.
# Note: we keep moderately blurry images (augmentation adds blur intentionally).
MIN_BLUR_SCORE = 30.0


# ---------------------------------------------------------------------------
# Detection functions
# ---------------------------------------------------------------------------

def is_infographic(img_bgr: np.ndarray) -> bool:
    """Return True if image looks like a chart/infographic with colored dots."""
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    saturation = img_hsv[:, :, 1]          # S channel, 0-255
    highly_saturated = np.sum(saturation > SATURATION_THRESHOLD)
    ratio = highly_saturated / saturation.size
    return ratio > MAX_SATURATED_RATIO


def is_blank(img_bgr: np.ndarray) -> bool:
    """Return True if image is nearly uniform (blank/white/black)."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return float(gray.std()) < MIN_PIXEL_STD


def is_too_blurry(img_bgr: np.ndarray) -> bool:
    """Return True if image is so blurry it's unrecognisable."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < MIN_BLUR_SCORE


def is_too_small(img_bgr: np.ndarray) -> bool:
    """Return True if image is below minimum resolution."""
    h, w = img_bgr.shape[:2]
    return w < MIN_DIMENSION or h < MIN_DIMENSION


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def clean():
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)

    exts = {".jpg", ".jpeg", ".png"}
    images = [p for p in SOURCE_DIR.iterdir() if p.suffix.lower() in exts]

    if not images:
        print(f"No images found in {SOURCE_DIR}")
        return

    print(f"Scanning {len(images)} images in {SOURCE_DIR.name}/")
    print()

    counts = {
        "infographic": 0,
        "blank":       0,
        "blurry":      0,
        "too_small":   0,
        "kept":        0,
    }

    rejected_log: list[tuple[str, str]] = []   # (filename, reason)

    for img_path in tqdm(images, desc="Cleaning", unit="img"):
        img = cv2.imread(str(img_path))

        # Can't read → reject
        if img is None:
            dest = REJECTED_DIR / img_path.name
            shutil.move(str(img_path), str(dest))
            counts["blank"] += 1
            rejected_log.append((img_path.name, "unreadable"))
            continue

        reason = None

        if is_too_small(img):
            reason = "too_small"
        elif is_blank(img):
            reason = "blank"
        elif is_infographic(img):
            reason = "infographic"
        elif is_too_blurry(img):
            reason = "blurry"

        if reason:
            dest = REJECTED_DIR / img_path.name
            shutil.move(str(img_path), str(dest))
            counts[reason] += 1
            rejected_log.append((img_path.name, reason))
        else:
            counts["kept"] += 1

    total_rejected = len(images) - counts["kept"]

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    print()
    print("=" * 55)
    print("CLEANING COMPLETE")
    print("=" * 55)
    print(f"  Total scanned      : {len(images)}")
    print(f"  Kept (clean)       : {counts['kept']}")
    print(f"  Rejected total     : {total_rejected}")
    print()
    print(f"  Breakdown of rejected:")
    print(f"    Infographic/dots : {counts['infographic']}")
    print(f"    Blank/uniform    : {counts['blank']}")
    print(f"    Too blurry       : {counts['blurry']}")
    print(f"    Too small        : {counts['too_small']}")
    print()
    print(f"  Rejected folder    : {REJECTED_DIR}")
    print("=" * 55)
    print()

    if rejected_log:
        # Write a log file so you can review what was removed and why
        log_path = REJECTED_DIR / "_rejection_log.txt"
        with open(log_path, "w") as f:
            f.write(f"{'Filename':<50}  Reason\n")
            f.write("-" * 65 + "\n")
            for fname, reason in rejected_log:
                f.write(f"{fname:<50}  {reason}\n")
        print(f"  Rejection log saved to: {log_path.name}")
        print()

    print("NEXT STEPS:")
    print("  1. Open garbage_rejected/ — confirm removals look correct.")
    print("  2. If anything was wrongly rejected, move it back to garbage/.")
    print("  3. Delete the garbage_augmented/ folder (built from dirty data).")
    print("  4. Re-run:  python augment_pakistani_garbage.py")


if __name__ == "__main__":
    clean()
