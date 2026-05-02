"""
Scrape Pakistani street garbage images for retraining dataset.

Output folder (separate from existing trained data):
    training/data/pakistani_dataset/garbage/

Run:
    pip install icrawler pillow
    python scrape_pakistani_garbage.py

After running:
    1. Open data/pakistani_dataset/garbage/ in Explorer
    2. Delete any clearly wrong images (maps, infographics, Western bins)
    3. Copy your existing 100 Pakistani images into the same folder
    4. This folder is then ready for Priority #3 (other class) and #5 (retrain)
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

OUTPUT_DIR = Path(__file__).parent / "data" / "pakistani_dataset" / "garbage"
TEMP_DIR   = Path(__file__).parent / "data" / "pakistani_dataset" / "_temp"

IMAGES_PER_QUERY = 100   # Bing caps at ~1000 per session; 100/query is reliable
MIN_DIMENSION    = 300   # px — reject thumbnails
MIN_FILE_SIZE    = 10    # KB
ALLOWED_MODES    = {"RGB", "RGBA", "L"}

# Pakistan-specific search queries — mix of English + Urdu transliterated
# to pull images from Pakistani news sites, local blogs, and social media.
QUERIES = [
    "Pakistan street garbage pile",
    "Karachi garbage dump road",
    "Lahore waste street garbage",
    "Islamabad garbage road pile",
    "Pakistan open drain garbage waste",
    "Pakistani bazaar kachra",
    "Pakistan kachra sadak",
    "kuda karachi street",
    "Pakistan ganda nala waste",
    "Pakistan plastic bags scattered road",
    "Pakistan garbage heap neighbourhood",
    "Pakistan solid waste municipal road",
    "Rawalpindi garbage street",
    "Faisalabad waste road",
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def is_valid_image(path: Path) -> tuple[bool, str]:
    """Return (valid, reason). Reason is empty string when valid."""
    # File size
    size_kb = path.stat().st_size / 1024
    if size_kb < MIN_FILE_SIZE:
        return False, f"too small ({size_kb:.1f} KB)"

    # Openable + dimensions + color mode
    try:
        img = Image.open(path)
        img.verify()           # catches truncated files
        img = Image.open(path) # reopen after verify (verify closes it)
        w, h = img.size
        mode = img.mode
    except Exception as e:
        return False, f"corrupt ({e})"

    if w < MIN_DIMENSION or h < MIN_DIMENSION:
        return False, f"too small ({w}x{h})"

    if mode not in ALLOWED_MODES:
        return False, f"unsupported mode ({mode})"

    return True, ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def scrape():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    seen_hashes: set[str] = set()

    # Hash all images already in OUTPUT_DIR so we don't re-add on re-runs
    existing = list(OUTPUT_DIR.glob("*.jpg")) + list(OUTPUT_DIR.glob("*.png"))
    for p in existing:
        seen_hashes.add(sha256(p))
    log.info(f"Found {len(existing)} existing images in output folder (hashes cached)")

    total_downloaded  = 0
    total_duplicates  = 0
    total_filtered    = 0
    total_kept        = 0

    for query_idx, query in enumerate(QUERIES, 1):
        log.info(f"[{query_idx}/{len(QUERIES)}] Querying: \"{query}\"")

        # Each query downloads into a fresh temp subfolder
        temp_query_dir = TEMP_DIR / f"q{query_idx:02d}"
        temp_query_dir.mkdir(parents=True, exist_ok=True)

        try:
            crawler = BingImageCrawler(
                storage={"root_dir": str(temp_query_dir)},
                log_level=logging.WARNING,   # suppress icrawler noise
            )
            crawler.crawl(
                keyword=query,
                max_num=IMAGES_PER_QUERY,
                min_size=(MIN_DIMENSION, MIN_DIMENSION),
                file_idx_offset=0,
            )
        except Exception as e:
            log.warning(f"  Crawler error for query '{query}': {e}")
            continue

        # Process downloaded files
        raw_files = (
            list(temp_query_dir.glob("*.jpg"))
            + list(temp_query_dir.glob("*.jpeg"))
            + list(temp_query_dir.glob("*.png"))
        )
        total_downloaded += len(raw_files)
        log.info(f"  Downloaded {len(raw_files)} raw files")

        kept_this_query = 0
        for raw in raw_files:
            # Validity check
            valid, reason = is_valid_image(raw)
            if not valid:
                total_filtered += 1
                raw.unlink(missing_ok=True)
                continue

            # Deduplication
            h = sha256(raw)
            if h in seen_hashes:
                total_duplicates += 1
                raw.unlink(missing_ok=True)
                continue

            seen_hashes.add(h)

            # Move to output with a clean sequential name
            dest_name = f"pak_scraped_{total_kept + 1:04d}{raw.suffix.lower()}"
            dest = OUTPUT_DIR / dest_name
            shutil.move(str(raw), str(dest))

            total_kept += 1
            kept_this_query += 1

        log.info(f"  Kept {kept_this_query} unique valid images")

        # Small delay between queries to avoid rate limiting
        time.sleep(2)

    # Clean up temp dir
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
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
    log.info("  1. Open the output folder in Explorer and remove any")
    log.info("     clearly wrong images (maps, Western bins, infographics).")
    log.info("  2. Copy your 100 existing Pakistani images into the same folder.")
    log.info("  3. Proceed to Priority #3 (expand 'other' class).")


if __name__ == "__main__":
    scrape()
