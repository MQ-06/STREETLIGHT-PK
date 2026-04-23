"""
Data augmentation for Pakistani garbage dataset.

Takes every image in:
    data/pakistani_dataset/garbage/

Generates 10 augmented variants per image into:
    data/pakistani_dataset/garbage_augmented/

The augmented folder contains BOTH the originals (copied) and all
generated variants so it can be used directly as a training source.

Run:
    pip install albumentations pillow opencv-python tqdm
    python augment_pakistani_garbage.py
"""

import random
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

import albumentations as A

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

INPUT_DIR  = Path(__file__).parent / "data" / "pakistani_dataset" / "garbage"
OUTPUT_DIR = Path(__file__).parent / "data" / "pakistani_dataset" / "garbage_augmented"

AUGMENTATIONS_PER_IMAGE = 10   # 332 originals × 10 = 3,320 augmented images
SEED = 42

# ---------------------------------------------------------------------------
# Augmentation pipeline
# ---------------------------------------------------------------------------
# Each call to this pipeline randomly picks a different combination of
# transforms, so every one of the 10 outputs per image looks distinct.
#
# p= controls probability that a given transform is applied in any one pass.
# Keeping most at p=0.5 means roughly half the transforms fire each time,
# giving varied combinations rather than always applying everything at once.

augment = A.Compose([

    # --- Geometry ---
    # Pakistani users photograph from different heights and angles.
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=20, p=0.6),
    A.RandomResizedCrop(
        size=(224, 224),
        scale=(0.7, 1.0),   # zoom in/out: simulates distance from garbage
        ratio=(0.75, 1.33),
        p=0.7
    ),
    A.Perspective(scale=(0.03, 0.08), p=0.3),

    # --- Lighting ---
    # Harsh Pakistani sunlight, evening light, or indoor artificial light.
    A.RandomBrightnessContrast(
        brightness_limit=0.4,
        contrast_limit=0.4,
        p=0.8
    ),
    A.RandomGamma(gamma_limit=(70, 130), p=0.4),

    # --- Color ---
    # Wet garbage vs dry, different garbage types have different hues.
    A.HueSaturationValue(
        hue_shift_limit=15,
        sat_shift_limit=30,
        val_shift_limit=20,
        p=0.6
    ),

    # --- Environmental conditions ---
    # Shadow from trees, buildings, overhead wires — very common on Pakistani streets.
    A.RandomShadow(
        shadow_roi=(0, 0.3, 1, 1),
        num_shadows_lower=1,
        num_shadows_upper=2,
        shadow_dimension=5,
        p=0.4
    ),
    # Smog/haze — Lahore, Karachi, Rawalpindi have heavy air pollution.
    A.RandomFog(fog_coef_lower=0.05, fog_coef_upper=0.2, alpha_coef=0.1, p=0.25),
    # Monsoon rain streaks on the camera lens.
    A.RandomRain(
        slant_lower=-10,
        slant_upper=10,
        drop_length=10,
        drop_width=1,
        drop_color=(180, 180, 180),
        blur_value=3,
        brightness_coefficient=0.85,
        rain_type="drizzle",
        p=0.2
    ),

    # --- Camera quality ---
    # Low-end phone cameras used by typical Pakistani users.
    A.GaussNoise(var_limit=(10, 50), mean=0, p=0.4),
    A.MotionBlur(blur_limit=5, p=0.3),          # phone camera movement
    A.ImageCompression(quality_lower=60, quality_upper=95, p=0.3),  # JPEG compression artifacts

    # Final resize to ensure all outputs are 224×224 (ResNet input size)
    A.Resize(224, 224),
])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_image_as_numpy(path: Path) -> np.ndarray | None:
    """Load image with OpenCV (handles more formats than PIL alone)."""
    img = cv2.imread(str(path))
    if img is None:
        return None
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def save_numpy_as_image(array: np.ndarray, path: Path):
    """Save RGB numpy array as image file."""
    img_bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path), img_bgr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def augment_dataset():
    random.seed(SEED)
    np.random.seed(SEED)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all input images
    exts = {".jpg", ".jpeg", ".png"}
    source_images = [p for p in INPUT_DIR.iterdir() if p.suffix.lower() in exts]

    if not source_images:
        print(f"No images found in {INPUT_DIR}")
        return

    print(f"Found {len(source_images)} source images in {INPUT_DIR.name}/")
    print(f"Generating {AUGMENTATIONS_PER_IMAGE} augmentations each")
    print(f"Expected output: ~{len(source_images) * (AUGMENTATIONS_PER_IMAGE + 1)} images")
    print(f"Output folder  : {OUTPUT_DIR}")
    print()

    failed       = 0
    aug_count    = 0
    copied_count = 0

    for src_path in tqdm(source_images, desc="Augmenting", unit="img"):
        image = load_image_as_numpy(src_path)
        if image is None:
            tqdm.write(f"  [SKIP] Could not read: {src_path.name}")
            failed += 1
            continue

        stem = src_path.stem

        # 1. Copy original into output folder unchanged
        dest_original = OUTPUT_DIR / src_path.name
        if not dest_original.exists():
            save_numpy_as_image(image, dest_original)
            copied_count += 1

        # 2. Generate augmented variants
        for i in range(1, AUGMENTATIONS_PER_IMAGE + 1):
            augmented = augment(image=image)["image"]
            out_name  = f"{stem}_aug{i:02d}.jpg"
            out_path  = OUTPUT_DIR / out_name
            save_numpy_as_image(augmented, out_path)
            aug_count += 1

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    total = copied_count + aug_count
    print()
    print("=" * 55)
    print("AUGMENTATION COMPLETE")
    print("=" * 55)
    print(f"  Source images      : {len(source_images)}")
    print(f"  Originals copied   : {copied_count}")
    print(f"  Augmented variants : {aug_count}")
    print(f"  Failed / skipped   : {failed}")
    print(f"  Total in output    : {total}")
    print(f"  Output folder      : {OUTPUT_DIR}")
    print("=" * 55)
    print()
    print("NEXT STEPS:")
    print("  1. Spot-check garbage_augmented/ — delete any clearly broken images.")
    print("  2. This folder is your Pakistani garbage training split.")
    print("  3. Proceed to Priority #3: expand the 'other' class.")


if __name__ == "__main__":
    augment_dataset()
