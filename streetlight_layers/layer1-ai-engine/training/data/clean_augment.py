"""
Clean augmentation - geometric transforms only, no blur, no color distortion.
Saves at high quality (JPEG 95).
"""
import os
import random
from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np

INPUT_DIR  = Path("pakistani_dataset/garbage")
OUTPUT_DIR = Path("pakistani_dataset/garbage")
TARGET     = 1500
SEED       = 42

random.seed(SEED)
np.random.seed(SEED)

def augment(img: Image.Image) -> Image.Image:
    """Apply one random clean transform."""
    choice = random.randint(0, 5)

    if choice == 0:
        # Horizontal flip
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    elif choice == 1:
        # Small rotation: -15 to +15 degrees, no expand (keeps size)
        angle = random.uniform(-15, 15)
        img = img.rotate(angle, resample=Image.BILINEAR, expand=False)

    elif choice == 2:
        # Random crop then resize back (zoom-in effect)
        w, h = img.size
        margin_x = int(w * 0.1)
        margin_y = int(h * 0.1)
        left   = random.randint(0, margin_x)
        top    = random.randint(0, margin_y)
        right  = w - random.randint(0, margin_x)
        bottom = h - random.randint(0, margin_y)
        img = img.crop((left, top, right, bottom)).resize((w, h), Image.BILINEAR)

    elif choice == 3:
        # Slight brightness: 0.85 to 1.15 only
        factor = random.uniform(0.85, 1.15)
        img = ImageEnhance.Brightness(img).enhance(factor)

    elif choice == 4:
        # Slight contrast: 0.85 to 1.15 only
        factor = random.uniform(0.85, 1.15)
        img = ImageEnhance.Contrast(img).enhance(factor)

    elif choice == 5:
        # Horizontal flip + small rotation combined
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        angle = random.uniform(-10, 10)
        img = img.rotate(angle, resample=Image.BILINEAR, expand=False)

    return img


def main():
    existing = sorted(INPUT_DIR.glob("*.jpg")) + sorted(INPUT_DIR.glob("*.jpeg")) + sorted(INPUT_DIR.glob("*.png"))
    existing = [p for p in existing if "aug_" not in p.name]  # skip already augmented
    current_total = len(list(OUTPUT_DIR.glob("*.*")))
    needed = TARGET - current_total

    if needed <= 0:
        print(f"Already have {current_total} images, target {TARGET} reached.")
        return

    print(f"Current: {current_total} | Target: {TARGET} | Generating: {needed}")

    generated = 0
    sources = existing.copy()
    random.shuffle(sources)
    idx = 0

    while generated < needed:
        src_path = sources[idx % len(sources)]
        idx += 1

        try:
            img = Image.open(src_path).convert("RGB")
        except Exception:
            continue

        aug_img = augment(img)
        out_name = f"aug_{generated:04d}_{src_path.stem}.jpg"
        out_path = OUTPUT_DIR / out_name
        aug_img.save(out_path, "JPEG", quality=95)  # high quality, no degradation
        generated += 1

        if generated % 100 == 0:
            print(f"  Generated {generated}/{needed}")

    print(f"Done. Total garbage images: {len(list(OUTPUT_DIR.glob('*.*')))}")


if __name__ == "__main__":
    main()
