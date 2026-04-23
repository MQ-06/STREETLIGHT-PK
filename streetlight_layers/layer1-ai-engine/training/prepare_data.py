"""
Data Preparation Script for StreetLight AI Engine
Splits images into train (70%), validation (15%), and test (15%) sets.

Usage:
    python prepare_data.py
"""

import shutil
import random
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

RAW_DATA_DIR = Path(__file__).parent / "data" / "pakistani_dataset"
TRAIN_DIR    = Path(__file__).parent / "data" / "train"
VAL_DIR      = Path(__file__).parent / "data" / "val"
TEST_DIR     = Path(__file__).parent / "data" / "test"

TRAIN_SPLIT = 0.70
VAL_SPLIT   = 0.15
# remaining 0.15 goes to test

CLASSES = ["pothole", "garbage", "other"]

VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
MIN_WIDTH  = 100
MIN_HEIGHT = 100


def validate_image(image_path: Path) -> Tuple[bool, str]:
    try:
        if not image_path.exists():
            return False, "File does not exist"
        if image_path.suffix not in VALID_EXTENSIONS:
            return False, f"Invalid extension: {image_path.suffix}"
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            w, h = img.size
            if w < MIN_WIDTH or h < MIN_HEIGHT:
                return False, f"Too small: {w}x{h}"
        return True, "Valid"
    except Exception as e:
        return False, f"Corrupted: {str(e)}"


def collect_valid_images(class_dir: Path, class_name: str) -> List[Path]:
    if not class_dir.exists():
        logger.warning(f"Directory not found: {class_dir}")
        return []

    valid, invalid = [], 0
    for img_path in class_dir.iterdir():
        if img_path.is_file():
            ok, msg = validate_image(img_path)
            if ok:
                valid.append(img_path)
            else:
                invalid += 1
                logger.warning(f"Skipping {img_path.name}: {msg}")

    logger.info(f"  {class_name}: {len(valid)} valid, {invalid} skipped")
    return valid


def split_and_copy(
    images: List[Path],
    class_name: str,
) -> Tuple[int, int, int]:
    random.shuffle(images)

    n = len(images)
    train_end = int(n * TRAIN_SPLIT)
    val_end   = train_end + int(n * VAL_SPLIT)

    splits = {
        'train': (TRAIN_DIR, images[:train_end]),
        'val':   (VAL_DIR,   images[train_end:val_end]),
        'test':  (TEST_DIR,  images[val_end:]),
    }

    counts = {}
    for split_name, (base_dir, subset) in splits.items():
        dest_dir = base_dir / class_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        for img_path in subset:
            shutil.copy2(img_path, dest_dir / img_path.name)
        counts[split_name] = len(subset)
        logger.info(f"  {class_name}/{split_name}: {len(subset)} images")

    return counts['train'], counts['val'], counts['test']


def print_statistics(stats: Dict[str, Dict[str, int]]):
    print("\n" + "=" * 65)
    print("DATASET STATISTICS")
    print("=" * 65)
    print(f"\n{'Class':<12} {'Train':<10} {'Val':<10} {'Test':<10} {'Total':<10}")
    print("-" * 65)

    totals = {'train': 0, 'val': 0, 'test': 0}
    for class_name in CLASSES:
        s = stats[class_name]
        total = s['train'] + s['val'] + s['test']
        print(f"{class_name:<12} {s['train']:<10} {s['val']:<10} {s['test']:<10} {total:<10}")
        for k in totals:
            totals[k] += s[k]

    grand = sum(totals.values())
    print("-" * 65)
    print(f"{'TOTAL':<12} {totals['train']:<10} {totals['val']:<10} {totals['test']:<10} {grand:<10}")
    print("=" * 65)
    print(f"\nSplit: {totals['train']/grand*100:.1f}% train  |  "
          f"{totals['val']/grand*100:.1f}% val  |  "
          f"{totals['test']/grand*100:.1f}% test")
    print(f"\n  Train : {TRAIN_DIR}")
    print(f"  Val   : {VAL_DIR}")
    print(f"  Test  : {TEST_DIR}\n")


def main():
    logger.info("StreetLight AI Engine - Data Preparation (70/15/15)")

    if not RAW_DATA_DIR.exists():
        logger.error(f"Source not found: {RAW_DATA_DIR}")
        return

    # Clean existing splits
    for d in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)

    logger.info("\nStep 1: Validating images...")
    all_images = {}
    for class_name in CLASSES:
        all_images[class_name] = collect_valid_images(
            RAW_DATA_DIR / class_name, class_name
        )

    total = sum(len(v) for v in all_images.values())
    if total == 0:
        logger.error("No valid images found.")
        return

    logger.info("\nStep 2: Splitting and copying...")
    stats = {}
    for class_name in CLASSES:
        images = all_images[class_name]
        if not images:
            stats[class_name] = {'train': 0, 'val': 0, 'test': 0}
            continue
        tr, va, te = split_and_copy(images, class_name)
        stats[class_name] = {'train': tr, 'val': va, 'test': te}

    print_statistics(stats)
    logger.info("Done. Next: python train.py")


if __name__ == "__main__":
    main()
