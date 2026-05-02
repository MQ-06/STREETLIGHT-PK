"""
CLIP-based semantic filter for Pakistani garbage dataset.

CLIP understands image content from text. This script scores every image
on how "garbage-like" it is vs how "non-garbage-like" it is, then moves
low-scoring images to a flagged folder for manual review.

How scoring works:
  garbage_score = avg(similarity to POSITIVE prompts)
                - avg(similarity to NEGATIVE prompts)

  score > 0  → image looks more like garbage than non-garbage → KEEP
  score < 0  → image looks more like food/film/street → FLAGGED

Input:   data/pakistani_dataset/garbage_augmented/
Flagged: data/pakistani_dataset/garbage_augmented_flagged/
Report:  data/pakistani_dataset/clip_scores.csv

Run:
    python clip_filter_garbage.py

After running:
    1. Check the score distribution printed at the end.
    2. Open garbage_augmented_flagged/ and verify — most should be non-garbage.
    3. Move any wrongly flagged images back to garbage_augmented/.
    4. Adjust SCORE_THRESHOLD if too many good images are flagged (raise it)
       or too many bad images slip through (lower it).
"""

import csv
import os
import shutil
from pathlib import Path

# Remove broken SSL_CERT_FILE env var that causes httpx to fail on Windows
os.environ.pop("SSL_CERT_FILE", None)

# Redirect HuggingFace model cache to D: drive — C: drive may lack space
# for the CLIP model (~605 MB). Must be set before importing transformers.
_hf_cache = Path("D:/hf_cache")
_hf_cache.mkdir(parents=True, exist_ok=True)
os.environ["HF_HOME"] = str(_hf_cache)

import torch
import numpy as np
from PIL import Image
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

INPUT_DIR   = Path(__file__).parent / "data" / "pakistani_dataset" / "garbage_augmented"
FLAGGED_DIR = Path(__file__).parent / "data" / "pakistani_dataset" / "garbage_augmented_flagged"
SCORES_CSV  = Path(__file__).parent / "data" / "pakistani_dataset" / "clip_scores.csv"

# Images with garbage_score below this are moved to flagged/
# 0.0 means "more non-garbage than garbage" → safe default
# Raise to 0.05 if too many bad images still slip through
# Lower to -0.05 if too many good images are being flagged
SCORE_THRESHOLD = 0.02

BATCH_SIZE = 32   # images processed at once — reduce to 16 if you get OOM

# ---------------------------------------------------------------------------
# Text prompts
# CLIP compares images against these descriptions.
# More specific prompts = better discrimination.
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Load CLIP
# ---------------------------------------------------------------------------

def load_clip():
    print("Loading CLIP model (downloads ~600 MB on first run)...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cache_path = "D:/hf_cache/hub/models--openai--clip-vit-base-patch32/snapshots/3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268"
    model     = CLIPModel.from_pretrained(cache_path, local_files_only=True)
    processor = CLIPProcessor.from_pretrained(cache_path, local_files_only=True)
    model.eval()
    model.to(device)
    print(f"  CLIP loaded on {device.upper()}")
    return model, processor, device


# ---------------------------------------------------------------------------
# Encode all text prompts once (reused for every image)
# ---------------------------------------------------------------------------

def encode_texts(model, processor, texts: list[str], device: str) -> torch.Tensor:
    inputs = processor(text=texts, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        out = model.get_text_features(**inputs)
    # transformers 5.x returns BaseModelOutputWithPooling, not a raw tensor
    features = out.pooler_output if not isinstance(out, torch.Tensor) else out
    return features / features.norm(dim=-1, keepdim=True)


# ---------------------------------------------------------------------------
# Score a batch of images
# ---------------------------------------------------------------------------

def score_batch(
    images: list,
    model,
    processor,
    pos_features: torch.Tensor,
    neg_features: torch.Tensor,
    device: str,
) -> list[float]:
    inputs = processor(images=images, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        out = model.get_image_features(**inputs)
    img_features = out.pooler_output if not isinstance(out, torch.Tensor) else out
    img_features = img_features / img_features.norm(dim=-1, keepdim=True)

    # cosine similarities: (batch, num_prompts)
    pos_sims = (img_features @ pos_features.T).cpu().numpy()  # (B, P)
    neg_sims = (img_features @ neg_features.T).cpu().numpy()  # (B, N)

    # garbage_score = mean positive similarity - mean negative similarity
    scores = pos_sims.mean(axis=1) - neg_sims.mean(axis=1)
    return scores.tolist()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    FLAGGED_DIR.mkdir(parents=True, exist_ok=True)

    exts = {".jpg", ".jpeg", ".png"}
    image_paths = [p for p in INPUT_DIR.iterdir() if p.suffix.lower() in exts]

    if not image_paths:
        print(f"No images found in {INPUT_DIR}")
        return

    print(f"\nFound {len(image_paths)} images in {INPUT_DIR.name}/")
    print(f"Score threshold : {SCORE_THRESHOLD}")
    print(f"Batch size      : {BATCH_SIZE}")
    print()

    model, processor, device = load_clip()

    # Encode text prompts once
    pos_features = encode_texts(model, processor, POSITIVE_PROMPTS, device)
    neg_features = encode_texts(model, processor, NEGATIVE_PROMPTS, device)
    print(f"  Encoded {len(POSITIVE_PROMPTS)} positive + {len(NEGATIVE_PROMPTS)} negative prompts\n")

    # Score all images in batches
    all_scores: list[tuple[Path, float]] = []   # (path, score)
    failed = 0

    for i in tqdm(range(0, len(image_paths), BATCH_SIZE), desc="Scoring", unit="batch"):
        batch_paths = image_paths[i : i + BATCH_SIZE]
        batch_images = []
        valid_paths  = []

        for p in batch_paths:
            try:
                img = Image.open(p).convert("RGB")
                batch_images.append(img)
                valid_paths.append(p)
            except Exception:
                failed += 1

        if not batch_images:
            continue

        try:
            scores = score_batch(
                batch_images, model, processor,
                pos_features, neg_features, device
            )
            all_scores.extend(zip(valid_paths, scores))
        except Exception as e:
            tqdm.write(f"  Batch error: {e}")
            failed += len(batch_images)

    # ---------------------------------------------------------------------------
    # Apply threshold — move flagged images
    # ---------------------------------------------------------------------------
    kept    = []
    flagged = []

    for path, score in all_scores:
        if score < SCORE_THRESHOLD:
            dest = FLAGGED_DIR / path.name
            shutil.move(str(path), str(dest))
            flagged.append((path.name, score))
        else:
            kept.append((path.name, score))

    # ---------------------------------------------------------------------------
    # Save CSV with all scores (useful for threshold tuning)
    # ---------------------------------------------------------------------------
    with open(SCORES_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "garbage_score", "status"])
        for name, score in kept:
            writer.writerow([name, f"{score:.4f}", "kept"])
        for name, score in flagged:
            writer.writerow([name, f"{score:.4f}", "flagged"])

    # ---------------------------------------------------------------------------
    # Score distribution (helps decide if threshold needs adjusting)
    # ---------------------------------------------------------------------------
    all_score_values = [s for _, s in all_scores]
    arr = np.array(all_score_values)

    print()
    print("=" * 55)
    print("CLIP FILTER COMPLETE")
    print("=" * 55)
    print(f"  Total scored    : {len(all_scores)}")
    print(f"  Kept            : {len(kept)}")
    print(f"  Flagged         : {len(flagged)}")
    print(f"  Failed/skipped  : {failed}")
    print()
    print(f"  Score distribution:")
    print(f"    Min   : {arr.min():.4f}")
    print(f"    Max   : {arr.max():.4f}")
    print(f"    Mean  : {arr.mean():.4f}")
    print(f"    Median: {np.median(arr):.4f}")
    print()

    # Show how many images fall in each score band
    bands = [(-1.0, -0.1), (-0.1, 0.0), (0.0, 0.1), (0.1, 0.2), (0.2, 1.0)]
    print(f"  Score bands:")
    for lo, hi in bands:
        count = int(((arr >= lo) & (arr < hi)).sum())
        bar   = "#" * min(40, int(count / max(len(arr), 1) * 200))
        print(f"    [{lo:+.1f} to {hi:+.1f}]  {count:4d}  {bar}")

    print()
    print(f"  Scores CSV      : {SCORES_CSV.name}")
    print(f"  Flagged folder  : {FLAGGED_DIR.name}/")
    print("=" * 55)
    print()
    print("NEXT STEPS:")
    print("  1. Open garbage_augmented_flagged/ — spot check ~20 images.")
    print("     Most should be food/films/streets/plants (correct rejections).")
    print("  2. If good garbage images were wrongly flagged: raise threshold")
    print(f"     above {SCORE_THRESHOLD} in SCORE_THRESHOLD at top of script, re-run.")
    print("  3. If bad images still in garbage_augmented/: lower threshold")
    print(f"     below {SCORE_THRESHOLD}, re-run.")
    print("  4. Once satisfied, garbage_augmented/ is your clean training set.")


if __name__ == "__main__":
    run()
