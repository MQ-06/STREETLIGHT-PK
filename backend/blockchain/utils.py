#blockchain/utils.py
import hashlib
import math
import logging
from pathlib import Path
from web3 import Web3

logger = logging.getLogger(__name__)


def hash_image_file(image_path: str) -> bytes:
   
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        # Read in chunks — safe for large images
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    image_hash = sha256.digest()  # 32 bytes
    logger.info(f"🔐 Image hash computed: 0x{image_hash.hex()[:16]}...")
    return image_hash


def hash_image_url(image_url: str) -> bytes:
 
    url_hash = hashlib.sha256(image_url.encode("utf-8")).digest()
    logger.info(f"🔐 URL hash computed: 0x{url_hash.hex()[:16]}...")
    return url_hash


def hash_location(latitude: float, longitude: float, precision: int = 2) -> bytes:
  
    if latitude is None or longitude is None:
        # Return zero hash if no location available
        logger.warning("⚠️ No location available — using zero location hash")
        return b'\x00' * 32

    # Round to reduce precision (privacy-preserving)
    approx_lat = round(latitude, precision)
    approx_lon = round(longitude, precision)

    # Create deterministic string representation
    location_str = f"{approx_lat},{approx_lon}"

    # keccak256 matches Solidity's keccak256() — consistent with contract
    location_hash = Web3.keccak(text=location_str)
    
    logger.info(
        f"📍 Location hash computed for approx "
        f"({approx_lat}, {approx_lon}): 0x{location_hash.hex()[:16]}..."
    )
    return bytes(location_hash)


def category_to_enum(category: str) -> int:
  
    mapping = {
        "POTHOLE": 0,
        "TRASH":   1,   # DB uses TRASH, contract uses GARBAGE
        "GARBAGE": 1,
        "OTHER":   2,
    }
    result = mapping.get(str(category).upper(), 2)
    logger.debug(f"📦 Category '{category}' → enum {result}")
    return result


def verification_type_to_enum(verification_status: str) -> int:
    if verification_status in ("AUTO_VERIFIED", "VERIFIED"): 
        return 0
    elif verification_status in ("OFFICER_APPROVED", "REVIEW_NEEDED"):
        return 1
    else:
        logger.warning(f"Unknown verification_status '{verification_status}' — defaulting to AUTO")
        return 0
