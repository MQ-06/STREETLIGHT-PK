"""
Scrape Pakistani "other" class images for retraining dataset.

"Other" = anything that is NOT garbage and NOT a pothole.
The model must learn to reject these as non-civic-issues.

Output folder:
    training/data/pakistani_dataset/other/

Run:
    pip install icrawler pillow
    python scrape_pakistani_other.py

After running:
    1. Run:  python clean_pakistani_dataset.py other
    2. Run:  python clip_filter_other.py
    3. Run:  python augment_dataset.py other
"""

import hashlib
import logging
import shutil
import time
from pathlib import Path

from PIL import Image
from icrawler.builtin import BingImageCrawler

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).parent / "data" / "pakistani_dataset" / "other"
TEMP_DIR   = Path(__file__).parent / "data" / "pakistani_dataset" / "_temp_other"

IMAGES_PER_QUERY = 80
MIN_DIMENSION    = 300
MIN_FILE_SIZE    = 10    # KB
ALLOWED_MODES    = {"RGB", "RGBA", "L"}

# ---------------------------------------------------------------------------
# Search queries
# Two groups:
#   A) Pakistani context — teaches model "Pakistani non-issue scene = other"
#   B) Generic rejectable — plants, food, screenshots, interiors
# ---------------------------------------------------------------------------

QUERIES = [
    # --- Pakistani urban context (most important) ---
    "Pakistan clean street no garbage",
    "Karachi clean road traffic",
    "Lahore market street crowd",
    "Pakistan bazaar shop building",
    "Pakistan residential neighbourhood clean",
    "Pakistan park garden green",
    "Pakistan mosque architecture",
    "Pakistan school college building",
    "Islamabad clean road",
    "Pakistan traffic jam cars road",
    "Pakistan building construction",
    "Pakistan bridge road infrastructure",

    # --- Generic rejectable content ---
    # These are things users might accidentally upload or test with
    "green plant flower garden",
    "food meal plate restaurant",
    "person portrait face outdoor",
    "indoor room interior home",
    "cat dog animal pet",
    "supermarket grocery shelves",
    "sky clouds blue",
    "computer laptop screen code",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def is_valid_image(path: Path) -> tuple[bool, str]:
    size_kb = path.stat().st_size / 1024
    if size_kb < MIN_FILE_SIZE:
        return False, f"too small ({size_kb:.1f} KB)"
    try:
        img = Image.open(path)
        img.verify()
        img = Image.open(path)
        w, h = img.size
        mode = img.mode
    except Exception as e:
        return False, f"corrupt ({e})"
    if w < MIN_DIMENSION or h < MIN_DIMENSION:
        return False, f"too small ({w}x{h})"
    if mode not in ALLOWED_MODES:
        return False, f"unsupported mode ({mode})"
    return True, ""


def scrape():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    seen_hashes: set[str] = set()
    existing = list(OUTPUT_DIR.glob("*.jpg")) + list(OUTPUT_DIR.glob("*.png"))
    for p in existing:
        seen_hashes.add(sha256(p))
    log.info(f"Found {len(existing)} existing images in output folder")

    total_downloaded = total_duplicates = total_filtered = total_kept = 0

    for idx, query in enumerate(QUERIES, 1):
        log.info(f"[{idx}/{len(QUERIES)}] Querying: \"{query}\"")

        temp_query_dir = TEMP_DIR / f"q{idx:02d}"
        temp_query_dir.mkdir(parents=True, exist_ok=True)

        try:
            crawler = BingImageCrawler(
                storage={"root_dir": str(temp_query_dir)},
                log_level=logging.WARNING,
            )
            crawler.crawl(
                keyword=query,
                max_num=IMAGES_PER_QUERY,
                min_size=(MIN_DIMENSION, MIN_DIMENSION),
                file_idx_offset=0,
            )
        except Exception as e:
            log.warning(f"  Crawler error: {e}")
            continue

        raw_files = (
            list(temp_query_dir.glob("*.jpg"))
            + list(temp_query_dir.glob("*.jpeg"))
            + list(temp_query_dir.glob("*.png"))
        )
        total_downloaded += len(raw_files)
        log.info(f"  Downloaded {len(raw_files)} raw files")

        kept_this_query = 0
        for raw in raw_files:
            valid, reason = is_valid_image(raw)
            if not valid:
                total_filtered += 1
                raw.unlink(missing_ok=True)
                continue

            h = sha256(raw)
            if h in seen_hashes:
                total_duplicates += 1
                raw.unlink(missing_ok=True)
                continue

            seen_hashes.add(h)
            dest = OUTPUT_DIR / f"other_scraped_{total_kept + 1:04d}{raw.suffix.lower()}"
            shutil.move(str(raw), str(dest))
            total_kept += 1
            kept_this_query += 1

        log.info(f"  Kept {kept_this_query} unique valid images")
        time.sleep(2)

    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    log.info("")
    log.info("=" * 55)
    log.info("SCRAPING COMPLETE")
    log.info("=" * 55)
    log.info(f"  Queries run        : {len(QUERIES)}")
    log.info(f"  Raw downloaded     : {total_downloaded}")
    log.info(f"  Filtered (bad)     : {total_filtered}")
    log.info(f"  Duplicates removed : {total_duplicates}")
    log.info(f"  Unique kept        : {total_kept}")
    log.info(f"  Output folder      : {OUTPUT_DIR}")
    log.info("=" * 55)
    log.info("")
    log.info("NEXT STEPS:")
    log.info("  1. python clean_pakistani_dataset.py other")
    log.info("  2. python clip_filter_other.py")
    log.info("  3. python augment_dataset.py other")


if __name__ == "__main__":
    scrape()
