"""
CLIP-based semantic filter for the "other" class dataset.

INVERTED logic compared to clip_filter_garbage.py:
  - For garbage class: KEEP images that look like garbage (score > threshold)
  - For other class:   KEEP images that do NOT look like garbage (score < threshold)

Any image in "other/" that scores high on garbage similarity gets flagged —
it means a plant photo accidentally looks like garbage, or a food image
looks similar enough to waste that the model would get confused.

Input:   data/pakistani_dataset/other/
Flagged: data/pakistani_dataset/other_flagged/
Report:  data/pakistani_dataset/clip_scores_other.csv

Run:
    python clip_filter_other.py
"""

import csv
import os
import shutil
from pathlib import Path

import torch
import numpy as np
from PIL import Image
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel

os.environ.pop("SSL_CERT_FILE", None)
os.environ["HF_HOME"] = str(Path("D:/hf_cache"))

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

INPUT_DIR   = Path(__file__).parent / "data" / "pakistani_dataset" / "other"
FLAGGED_DIR = Path(__file__).parent / "data" / "pakistani_dataset" / "other_flagged"
SCORES_CSV  = Path(__file__).parent / "data" / "pakistani_dataset" / "clip_scores_other.csv"

# Images scoring ABOVE this on garbage similarity are flagged.
# They accidentally look too garbage-like to be a clean "other" example.
# 0.02 is a good starting point — same as garbage filter threshold.
GARBAGE_SCORE_THRESHOLD = 0.02

BATCH_SIZE = 32

# Reusing the same prompt sets as garbage filter
POSITIVE_PROMPTS = [
    "street garbage pile on road",
    "trash and waste on Pakistani road",
    "plastic bags and garbage on dusty street",
    "litter scattered on ground",
    "garbage heap near drain",
    "waste dump on road",
    "rubbish on street",
    "garbage on dirty road",
]

NEGATIVE_PROMPTS = [
    "food and restaurant meal on plate",
    "people in market or bazaar",
    "film poster or movie advertisement",
    "green plant and tree",
    "clean empty street with no garbage",
    "building and architecture",
    "person standing smiling",
    "computer code on screen",
    "car and vehicle on road",
    "interior of a room",
]


def load_clip():
    print("Loading CLIP model...")
    device    = "cuda" if torch.cuda.is_available() else "cpu"
    cache_path = "D:/hf_cache/hub/models--openai--clip-vit-base-patch32/snapshots/3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268"
    model     = CLIPModel.from_pretrained(cache_path, local_files_only=True)
    processor = CLIPProcessor.from_pretrained(cache_path, local_files_only=True)
    model.eval()
    model.to(device)
    print(f"  CLIP loaded on {device.upper()}")
    return model, processor, device


def encode_texts(model, processor, texts, device):
    inputs = processor(text=texts, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        out = model.get_text_features(**inputs)
    features = out.pooler_output if not isinstance(out, torch.Tensor) else out
    return features / features.norm(dim=-1, keepdim=True)


def score_batch(images, model, processor, pos_features, neg_features, device):
    inputs = processor(images=images, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        out = model.get_image_features(**inputs)
    img_features = out.pooler_output if not isinstance(out, torch.Tensor) else out
    img_features = img_features / img_features.norm(dim=-1, keepdim=True)
    pos_sims = (img_features @ pos_features.T).cpu().numpy()
    neg_sims = (img_features @ neg_features.T).cpu().numpy()
    return (pos_sims.mean(axis=1) - neg_sims.mean(axis=1)).tolist()


def run():
    FLAGGED_DIR.mkdir(parents=True, exist_ok=True)

    exts = {".jpg", ".jpeg", ".png"}
    image_paths = [p for p in INPUT_DIR.iterdir() if p.suffix.lower() in exts]

    if not image_paths:
        print(f"No images found in {INPUT_DIR}")
        return

    print(f"\nFound {len(image_paths)} images in {INPUT_DIR.name}/")
    print(f"Garbage score threshold : {GARBAGE_SCORE_THRESHOLD}")
    print(f"Logic: KEEP if score < {GARBAGE_SCORE_THRESHOLD} (image does NOT look like garbage)")
    print(f"       FLAG if score >= {GARBAGE_SCORE_THRESHOLD} (image looks too garbage-like)")
    print()

    model, processor, device = load_clip()
    pos_features = encode_texts(model, processor, POSITIVE_PROMPTS, device)
    neg_features = encode_texts(model, processor, NEGATIVE_PROMPTS, device)
    print(f"  Encoded {len(POSITIVE_PROMPTS)} positive + {len(NEGATIVE_PROMPTS)} negative prompts\n")

    all_scores = []
    failed = 0

    for i in tqdm(range(0, len(image_paths), BATCH_SIZE), desc="Scoring", unit="batch"):
        batch_paths  = image_paths[i : i + BATCH_SIZE]
        batch_images = []
        valid_paths  = []

        for p in batch_paths:
            try:
                batch_images.append(Image.open(p).convert("RGB"))
                valid_paths.append(p)
            except Exception:
                failed += 1

        if not batch_images:
            continue

        try:
            scores = score_batch(batch_images, model, processor, pos_features, neg_features, device)
            all_scores.extend(zip(valid_paths, scores))
        except Exception as e:
            tqdm.write(f"  Batch error: {e}")
            failed += len(batch_images)

    # ---------------------------------------------------------------------------
    # Apply inverted threshold: flag images that look TOO garbage-like
    # ---------------------------------------------------------------------------
    kept    = []
    flagged = []

    for path, score in all_scores:
        if score >= GARBAGE_SCORE_THRESHOLD:
            dest = FLAGGED_DIR / path.name
            shutil.move(str(path), str(dest))
            flagged.append((path.name, score))
        else:
            kept.append((path.name, score))

    with open(SCORES_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "garbage_score", "status"])
        for name, score in kept:
            writer.writerow([name, f"{score:.4f}", "kept"])
        for name, score in flagged:
            writer.writerow([name, f"{score:.4f}", "flagged"])

    arr = np.array([s for _, s in all_scores])

    print()
    print("=" * 55)
    print("CLIP FILTER (OTHER CLASS) COMPLETE")
    print("=" * 55)
    print(f"  Total scored    : {len(all_scores)}")
    print(f"  Kept            : {len(kept)}   (score < {GARBAGE_SCORE_THRESHOLD})")
    print(f"  Flagged         : {len(flagged)}  (score >= {GARBAGE_SCORE_THRESHOLD}, too garbage-like)")
    print(f"  Failed/skipped  : {failed}")
    print()
    print(f"  Score distribution:")
    print(f"    Min   : {arr.min():.4f}")
    print(f"    Max   : {arr.max():.4f}")
    print(f"    Mean  : {arr.mean():.4f}")
    print(f"    Median: {np.median(arr):.4f}")
    print()
    bands = [(-1.0, -0.1), (-0.1, 0.0), (0.0, 0.02), (0.02, 0.1), (0.1, 1.0)]
    print(f"  Score bands (threshold at 0.02):")
    for lo, hi in bands:
        count  = int(((arr >= lo) & (arr < hi)).sum())
        marker = " <- flagged" if lo >= GARBAGE_SCORE_THRESHOLD else " <- kept"
        print(f"    [{lo:+.2f} to {hi:+.2f}]  {count:4d}  {marker}")
    print()
    print(f"  Scores CSV      : {SCORES_CSV.name}")
    print(f"  Flagged folder  : {FLAGGED_DIR.name}/")
    print("=" * 55)
    print()
    print("NEXT STEPS:")
    print("  1. Open other_flagged/ — confirm flagged images look garbage-like.")
    print("  2. If clean 'other' images were wrongly flagged: lower GARBAGE_SCORE_THRESHOLD.")
    print("  3. Run:  python augment_dataset.py other")


if __name__ == "__main__":
    run()
