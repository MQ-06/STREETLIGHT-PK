"""
Data augmentation for any class in the Pakistani dataset.

Usage:
    python augment_dataset.py garbage   # augments other/ -> other_augmented/
    python augment_dataset.py other     # augments other/ -> other_augmented/

Takes every image in:
    data/pakistani_dataset/<class>/

Generates augmented variants into:
    data/pakistani_dataset/<class>_augmented/

Run:
    pip install albumentations pillow opencv-python tqdm
    python augment_dataset.py other
"""

import sys
import random
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

import albumentations as A

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent / "data" / "pakistani_dataset"

if len(sys.argv) < 2:
    print("Usage: python augment_dataset.py <class_folder>")
    print("  e.g: python augment_dataset.py other")
    print("  e.g: python augment_dataset.py garbage")
    sys.exit(1)

CLASS_NAME = sys.argv[1]
INPUT_DIR  = BASE_DIR / CLASS_NAME
OUTPUT_DIR = BASE_DIR / f"{CLASS_NAME}_augmented"

# For "other" class we generate fewer variants — diversity comes naturally
# from having many different content types (plants, food, buildings, etc.)
# For "garbage" we need 10x because content is repetitive.
AUGMENTATIONS_PER_IMAGE = 5 if CLASS_NAME == "other" else 10

SEED = 42

# ---------------------------------------------------------------------------
# Augmentation pipeline
# Transforms are content-agnostic (geometry + lighting + noise) so they
# work equally well for garbage, other, and pothole classes.
# ---------------------------------------------------------------------------

augment = A.Compose([

    # Geometry
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=20, p=0.6),
    A.RandomResizedCrop(
        size=(224, 224),
        scale=(0.7, 1.0),
        ratio=(0.75, 1.33),
        p=0.7
    ),
    A.Perspective(scale=(0.03, 0.08), p=0.3),

    # Lighting — covers Pakistani harsh sun, evening, and indoor conditions
    A.RandomBrightnessContrast(brightness_limit=0.4, contrast_limit=0.4, p=0.8),
    A.RandomGamma(gamma_limit=(70, 130), p=0.4),

    # Color — wet vs dry, different times of day
    A.HueSaturationValue(
        hue_shift_limit=15,
        sat_shift_limit=30,
        val_shift_limit=20,
        p=0.6
    ),

    # Environmental — shadows, smog, rain, camera noise
    A.RandomShadow(
        shadow_roi=(0, 0.3, 1, 1),
        num_shadows_lower=1,
        num_shadows_upper=2,
        shadow_dimension=5,
        p=0.4
    ),
    A.RandomFog(fog_coef_lower=0.05, fog_coef_upper=0.2, alpha_coef=0.1, p=0.2),
    A.RandomRain(
        slant_lower=-10,
        slant_upper=10,
        drop_length=10,
        drop_width=1,
        drop_color=(180, 180, 180),
        blur_value=3,
        brightness_coefficient=0.85,
        rain_type="drizzle",
        p=0.15
    ),

    # Camera quality — low-end phone cameras
    A.GaussNoise(var_limit=(10, 50), mean=0, p=0.4),
    A.MotionBlur(blur_limit=5, p=0.3),
    A.ImageCompression(quality_lower=60, quality_upper=95, p=0.3),

    # Final resize to ResNet input size
    A.Resize(224, 224),
])


def load_image(path: Path) -> np.ndarray | None:
    img = cv2.imread(str(path))
    if img is None:
        return None
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def save_image(array: np.ndarray, path: Path):
    cv2.imwrite(str(path), cv2.cvtColor(array, cv2.COLOR_RGB2BGR))


def augment_dataset():
    random.seed(SEED)
    np.random.seed(SEED)

    if not INPUT_DIR.exists():
        print(f"Input folder not found: {INPUT_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    exts = {".jpg", ".jpeg", ".png"}
    sources = [p for p in INPUT_DIR.iterdir() if p.suffix.lower() in exts]

    if not sources:
        print(f"No images found in {INPUT_DIR}")
        sys.exit(1)

    print(f"Class              : {CLASS_NAME}")
    print(f"Source images      : {len(sources)}")
    print(f"Augmentations each : {AUGMENTATIONS_PER_IMAGE}")
    print(f"Expected output    : ~{len(sources) * (AUGMENTATIONS_PER_IMAGE + 1)}")
    print(f"Output folder      : {OUTPUT_DIR}")
    print()

    failed = copied = aug_count = 0

    for src in tqdm(sources, desc=f"Augmenting {CLASS_NAME}", unit="img"):
        image = load_image(src)
        if image is None:
            tqdm.write(f"  [SKIP] {src.name}")
            failed += 1
            continue

        # Copy original
        dest_orig = OUTPUT_DIR / src.name
        if not dest_orig.exists():
            save_image(image, dest_orig)
            copied += 1

        # Generate variants
        for i in range(1, AUGMENTATIONS_PER_IMAGE + 1):
            out_path = OUTPUT_DIR / f"{src.stem}_aug{i:02d}.jpg"
            save_image(augment(image=image)["image"], out_path)
            aug_count += 1

    total = copied + aug_count
    print()
    print("=" * 55)
    print(f"AUGMENTATION COMPLETE — {CLASS_NAME.upper()}")
    print("=" * 55)
    print(f"  Source images      : {len(sources)}")
    print(f"  Originals copied   : {copied}")
    print(f"  Augmented variants : {aug_count}")
    print(f"  Failed / skipped   : {failed}")
    print(f"  Total in output    : {total}")
    print(f"  Output folder      : {OUTPUT_DIR}")
    print("=" * 55)
    print()
    print("NEXT STEPS:")
    print(f"  Run the CLIP filter on {CLASS_NAME}_augmented/ to clean the output:")
    if CLASS_NAME == "other":
        print(f"  python clip_filter_other.py   (flags images that look garbage-like)")
    else:
        print(f"  python clip_filter_garbage.py {CLASS_NAME}_augmented")


if __name__ == "__main__":
    augment_dataset()
