#blockchain/blockchain_service.py
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware


from blockchain.utils import (
    hash_image_url,
    hash_location,
    category_to_enum,
    verification_type_to_enum,
)

logger = logging.getLogger(__name__)

# ── ABI path ──────────────────────────────────────────────────────────────────
# Points to compiled artifact from Hardhat
_ABI_PATH = (
    Path(__file__).resolve().parent.parent.parent  # project root
    / "blockchain-layer"
    / "artifacts"
    / "contracts"
    / "streetLight.sol"
    / "StreetLight.json"
)


class BlockchainService:

    def __init__(self):
        self.enabled = os.getenv("BLOCKCHAIN_ENABLED", "false").lower() == "true"
        self.w3: Optional[Web3] = None
        self.contract = None
        self.account = None

        if not self.enabled:
            logger.warning("Blockchain DISABLED — set BLOCKCHAIN_ENABLED=true in .env to enable")
            return

        self._initialize()

    def _initialize(self):
        """Connect to blockchain and load contract."""
        try:
            rpc_url = os.getenv("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")
            private_key = os.getenv("DEPLOYER_PRIVATE_KEY", "")
            contract_address = os.getenv("CONTRACT_ADDRESS", "")

            # ── Validate config ───────────────────────────────────────────────
            if not private_key:
                raise ValueError("DEPLOYER_PRIVATE_KEY not set in .env")
            if not contract_address:
                raise ValueError("CONTRACT_ADDRESS not set in .env")

            # ── Connect to node ───────────────────────────────────────────────
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))

            # POA middleware needed for some testnets (Sepolia may need this)
            self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

            if not self.w3.is_connected():
                raise ConnectionError(f"Cannot connect to blockchain at {rpc_url}")

            logger.info(f"Connected to blockchain: {rpc_url}")
            logger.info(f"   Chain ID: {self.w3.eth.chain_id}")

            # ── Load account ──────────────────────────────────────────────────
            self.account = self.w3.eth.account.from_key(private_key)
            logger.info(f"   Deployer address: {self.account.address}")

            # ── Load ABI ──────────────────────────────────────────────────────
            if not _ABI_PATH.exists():
                raise FileNotFoundError(
                    f"ABI not found at {_ABI_PATH}. "
                    f"Run 'npx hardhat compile' in blockchain-layer/"
                )

            with open(_ABI_PATH) as f:
                artifact = json.load(f)
            abi = artifact["abi"]

            # ── Load contract ─────────────────────────────────────────────────
            checksum_address = Web3.to_checksum_address(contract_address)
            self.contract = self.w3.eth.contract(
                address=checksum_address,
                abi=abi
            )

            logger.info(f"   Contract loaded: {checksum_address}")
            logger.info("✅ BlockchainService fully initialized")

        except Exception as e:
            logger.error(f"❌ BlockchainService initialization failed: {e}")
            logger.warning("⚠️  Blockchain calls will be skipped (no crash)")
            self.enabled = False
            self.w3 = None
            self.contract = None

    # ── PUBLIC API ─────────────────────────────────────────────────────────────

    def register_complaint(
        self,
        complaint_id: int,
        image_url: str,
        category: str,
        latitude: Optional[float],
        longitude: Optional[float],
        verification_status: str,
        ai_score: float,
        final_score: float,
    ) -> Dict:
       
        if not self.enabled or self.contract is None:
            return self._disabled_response("register", complaint_id)

        try:
            logger.info("=" * 50)
            logger.info(f"⛓️  BLOCKCHAIN: Registering complaint #{complaint_id}")
            logger.info(f"   Category: {category} | Status: {verification_status}")
            logger.info(f"   AI Score: {ai_score} | Final Score: {final_score}")
            logger.info("=" * 50)

            # ── Prepare hashes ────────────────────────────────────────────────
            image_hash_bytes  = hash_image_url(image_url)
            location_hash_bytes = hash_location(latitude, longitude)

            # ── Convert to Solidity types ─────────────────────────────────────
            image_hash_bytes32    = image_hash_bytes       # already 32 bytes
            location_hash_bytes32 = location_hash_bytes    # already 32 bytes
            issue_category_enum   = category_to_enum(category)
            verification_type_enum = verification_type_to_enum(verification_status)
            ai_score_uint8        = min(int(ai_score), 100)
            final_score_uint8     = min(int(final_score), 100)

            # ── Build transaction ─────────────────────────────────────────────
            nonce = self.w3.eth.get_transaction_count(self.account.address)

            tx = self.contract.functions.registerComplaint(
                complaint_id,
                image_hash_bytes32,
                issue_category_enum,
                location_hash_bytes32,
                verification_type_enum,
                ai_score_uint8,
                final_score_uint8,
            ).build_transaction({
                "from":     self.account.address,
                "nonce":    nonce,
                "gas":      300000,
                "gasPrice": self.w3.eth.gas_price,
            })

            # ── Sign and send ─────────────────────────────────────────────────
            signed_tx = self.w3.eth.account.sign_transaction(
                tx, private_key=os.getenv("DEPLOYER_PRIVATE_KEY")
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # ── Wait for confirmation ─────────────────────────────────────────
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status != 1:
                raise Exception(f"Transaction reverted! Hash: {tx_hash.hex()}")

            logger.info(f"   BLOCKCHAIN: Complaint #{complaint_id} registered!")
            logger.info(f"   TX Hash:      0x{tx_hash.hex()}")
            logger.info(f"   Block Number: {receipt.blockNumber}")

            return {
                "success":           True,
                "tx_hash":           f"0x{tx_hash.hex()}",
                "block_number":      receipt.blockNumber,
                "complaint_id":      complaint_id,
                "image_hash":        f"0x{image_hash_bytes.hex()}",
                "verification_type": verification_status,
                "ai_score":          ai_score_uint8,
                "final_score":       final_score_uint8,
            }

        except Exception as e:
            logger.error(f"❌ BLOCKCHAIN: register_complaint failed: {e}")
            return {
                "success":      False,
                "complaint_id": complaint_id,
                "error":        str(e),
            }

    def mark_resolved(
        self,
        complaint_id: int,
        resolution_note: str = "Issue resolved by municipality",
    ) -> Dict:
        """
        Second on-chain transition after citizen/officer resolution.
        Full contract tx path is optional; callers must handle success=False.
        """
        if not self.enabled or self.contract is None:
            return self._disabled_response("resolve", complaint_id)

        logger.warning(
            "Blockchain enabled but markResolved contract call is not implemented "
            "in this build — complaint_id=%s",
            complaint_id,
        )
        return {
            "success": False,
            "complaint_id": complaint_id,
            "error": "markResolved transaction not implemented",
            "skipped": True,
        }

    def get_complaint_proof(self, complaint_id: int) -> Dict:
       
        if not self.enabled or self.contract is None:
            return self._disabled_response("get", complaint_id)

        try:
            # Read-only — no transaction needed
            result = self.contract.functions.getComplaint(complaint_id).call()

            # Map tuple to readable dict
            status_map = {0: "VERIFIED", 1: "RESOLVED"}
            type_map   = {0: "AUTO", 1: "OFFICER"}
            cat_map    = {0: "POTHOLE", 1: "GARBAGE", 2: "OTHER"}

            return {
                "success":           True,
                "complaint_id":      result[0],
                "image_hash":        f"0x{result[1].hex()}",
                "issue_category":    cat_map.get(result[2], "UNKNOWN"),
                "verified_at":       result[3],
                "resolved_at":       result[4],
                "location_hash":     f"0x{result[5].hex()}",
                "verification_type": type_map.get(result[6], "UNKNOWN"),
                "status":            status_map.get(result[7], "UNKNOWN"),
                "ai_score":          result[8],
                "final_score":       result[9],
                "exists":            result[10],
            }

        except Exception as e:
            logger.error(f"❌ BLOCKCHAIN: get_complaint_proof failed: {e}")
            return {
                "success":      False,
                "complaint_id": complaint_id,
                "error":        str(e),
            }

    def get_stats(self) -> Dict:
        """Get total/resolved/pending stats from contract."""
        if not self.enabled or self.contract is None:
            return {"success": False, "error": "Blockchain disabled"}

        try:
            total, resolved, pending = self.contract.functions.getStats().call()
            return {
                "success":  True,
                "total":    total,
                "resolved": resolved,
                "pending":  pending,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def is_healthy(self) -> bool:
        """Quick health check — is blockchain connected?"""
        if not self.enabled or self.w3 is None:
            return False
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    # ── PRIVATE HELPERS ────────────────────────────────────────────────────────

    def _disabled_response(self, operation: str, complaint_id: int) -> Dict:
        """Return a graceful response when blockchain is disabled."""
        logger.warning(
            f"⚠️  Blockchain DISABLED — skipping '{operation}' "
            f"for complaint #{complaint_id}"
        )
        return {
            "success":      False,
            "complaint_id": complaint_id,
            "error":        "Blockchain disabled (BLOCKCHAIN_ENABLED=false)",
            "skipped":      True,
        }


# ── Module-level singleton ─────────────────────────────────────────────────────
# Import this instance everywhere — initialized once at startup
blockchain_service = BlockchainService()