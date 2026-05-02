"""
Preprocessing script — run after prepare_data.py, before zipping for Colab.
- Converts all images to RGB
- Resizes to max 512x512 (preserving aspect ratio)
- Removes corrupt files
- Saves in-place at JPEG quality 95
"""

from pathlib import Path
from PIL import Image
import sys

DATA_DIR   = Path(__file__).parent / "data"
SPLITS     = ["train", "val", "test"]
CLASSES    = ["garbage", "pothole", "other"]
MAX_SIZE   = 512

total_ok = 0
total_removed = 0
total_converted = 0

for split in SPLITS:
    for cls in CLASSES:
        folder = DATA_DIR / split / cls
        if not folder.exists():
            continue

        for img_path in list(folder.iterdir()):
            if not img_path.is_file():
                continue

            try:
                with Image.open(img_path) as img:
                    changed = False

                    # Convert to RGB if needed (handles grayscale, RGBA, palette)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                        changed = True
                        total_converted += 1

                    # Resize if larger than MAX_SIZE on either dimension
                    w, h = img.size
                    if w > MAX_SIZE or h > MAX_SIZE:
                        img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
                        changed = True

                    # Save as JPEG with high quality
                    out_path = img_path.with_suffix(".jpg")
                    img.save(out_path, "JPEG", quality=95)

                    # Remove original if it was a non-jpg (e.g. .png → .jpg)
                    if img_path.suffix.lower() != ".jpg":
                        img_path.unlink()

                total_ok += 1

            except Exception as e:
                print(f"  Removing corrupt file: {img_path.name} ({e})")
                img_path.unlink()
                total_removed += 1

        count = len(list(folder.glob("*.jpg")))
        print(f"  {split}/{cls}: {count} images")

print(f"\nDone.")
print(f"  Processed : {total_ok}")
print(f"  Converted to RGB: {total_converted}")
print(f"  Removed corrupt : {total_removed}")
print(f"\nNow zip: train/ val/ test/ and upload to Google Drive.")
