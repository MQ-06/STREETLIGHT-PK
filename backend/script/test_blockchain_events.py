"""
test_blockchain_events.py
=========================
Tests that StreetLight smart contract emits:
  ✅ Event #1 — ComplaintVerified  (via registerComplaint)
  ✅ Event #2 — ComplaintResolved  (via markResolved)

Run from project root:
    python test_blockchain_events.py

Prerequisites:
    pip install web3 python-dotenv
    Terminal 1: npx hardhat node
    Terminal 2: npx hardhat run scripts/deploy.js --network localhost
    (then add CONTRACT_ADDRESS=0x... to .env)
"""

import os
import sys
import json
import hashlib
import time
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
RPC_URL          = os.getenv("BLOCKCHAIN_RPC_URL",   "http://127.0.0.1:8545")
PRIVATE_KEY      = os.getenv("DEPLOYER_PRIVATE_KEY", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS",     "")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

IMAGE_PATH = (
    BASE_DIR
    / "backend"
    / "uploads"
    / "reports"
    / "2026"
    / "02"
    / "28"
    / "pothole.jpg"
)

ABI_PATH = (
    BASE_DIR
    / "blockchain-layer"
    / "artifacts"
    / "contracts"
    / "streetLight.sol"
    / "StreetLight.json"
)

# ── ANSI colours ──────────────────────────────────────────────────────────────
G  = "\033[92m"   # green
R  = "\033[91m"   # red
Y  = "\033[93m"   # yellow
C  = "\033[96m"   # cyan
Z  = "\033[0m"    # reset
B  = "\033[1m"    # bold

PASS = f"{G}✅ PASS{Z}"
FAIL = f"{R}❌ FAIL{Z}"

results = []

def record(name, passed, detail=""):
    results.append({"name": name, "passed": passed, "detail": detail})
    print(f"  {PASS if passed else FAIL}  {name}")
    if detail:
        print(f"         {C}{detail}{Z}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_image(path: Path) -> bytes:
    if path.exists():
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        d = sha.digest()
        print(f"  {C}🔐 Image hash (file): 0x{d.hex()[:20]}...{Z}")
        return d
    else:
        d = hashlib.sha256(str(path).encode()).digest()
        print(f"  {Y}⚠️  Image not found — using URL-style hash fallback{Z}")
        print(f"  {C}   0x{d.hex()[:20]}...{Z}")
        return d

def hash_location(lat, lon, precision=2) -> bytes:
    s = f"{round(lat, precision)},{round(lon, precision)}"
    return bytes(Web3.keccak(text=s))

def load_abi():
    if not ABI_PATH.exists():
        sys.exit(f"\n{R}ABI not found: {ABI_PATH}\nRun: npx hardhat compile{Z}\n")
    with open(ABI_PATH) as f:
        return json.load(f)["abi"]

def connect():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    if not w3.is_connected():
        sys.exit(f"\n{R}Cannot connect to {RPC_URL}\nRun: npx hardhat node{Z}\n")
    return w3

def load_contract(w3, abi):
    if not CONTRACT_ADDRESS:
        sys.exit(f"\n{R}CONTRACT_ADDRESS not in .env\nDeploy first then add it.{Z}\n")
    return w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi
    )

def send_tx(w3, account, fn_call, gas):
    nonce  = w3.eth.get_transaction_count(account.address)
    tx     = fn_call.build_transaction({
        "from": account.address, "nonce": nonce,
        "gas": gas, "gasPrice": w3.eth.gas_price,
    })
    signed  = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)


# ═════════════════════════════════════════════════════════════════════════════
def run_tests():
    print(f"\n{B}{C}{'='*60}{Z}")
    print(f"{B}{C}  StreetLight — Blockchain Event Tests{Z}")
    print(f"{B}{C}{'='*60}{Z}\n")

    print(f"{Y}[SETUP]{Z}")
    w3       = connect()
    abi      = load_abi()
    contract = load_contract(w3, abi)
    account  = w3.eth.account.from_key(PRIVATE_KEY)

    print(f"  RPC      : {RPC_URL}")
    print(f"  Chain ID : {w3.eth.chain_id}")
    print(f"  Account  : {account.address}")
    print(f"  Contract : {CONTRACT_ADDRESS}")

    # Unique ID per run so re-runs never collide
    complaint_id   = int(time.time()) % 100_000
    image_hash_b32 = hash_image(IMAGE_PATH)
    loc_hash_b32   = hash_location(31.5497, 74.3436)  # Lahore

    # Solidity enums
    POTHOLE = 0   # IssueCategory
    AUTO    = 0   # VerificationType
    ai_score, final_score = 88, 91

    print(f"  complaint_id = {complaint_id}  (auto-generated, unique per run)\n")

    # ── TEST 1: registerComplaint → ComplaintVerified ─────────────────────────
    print(f"\n{B}{Y}[TEST 1] registerComplaint() → ComplaintVerified event{Z}")
    try:
        rec = send_tx(
            w3, account,
            contract.functions.registerComplaint(
                complaint_id, image_hash_b32, POTHOLE,
                loc_hash_b32, AUTO, ai_score, final_score,
            ),
            gas=300_000,
        )

        record("Transaction status == 1", rec.status == 1,
               f"TX: 0x{rec.transactionHash.hex()}")

        evs = contract.events.ComplaintVerified().process_receipt(rec)
        record("ComplaintVerified event emitted", len(evs) > 0,
               f"count: {len(evs)}")

        if evs:
            ev = evs[0]["args"]
            print(f"\n  {B}📡 ComplaintVerified args:{Z}")
            print(f"    complaintId      = {ev['complaintId']}")
            print(f"    imageHash        = 0x{ev['imageHash'].hex()}")
            print(f"    issueCategory    = {ev['issueCategory']}  (0=POTHOLE)")
            print(f"    timestamp        = {ev['timestamp']}")
            print(f"    verificationType = {ev['verificationType']}  (0=AUTO)")
            print(f"    aiScore          = {ev['aiScore']}")
            print(f"    finalScore       = {ev['finalScore']}")
            print(f"    blockNumber      = {rec.blockNumber}\n")

            record("complaintId correct",        ev["complaintId"] == complaint_id)
            record("imageHash correct",          ev["imageHash"] == image_hash_b32)
            record("issueCategory == POTHOLE(0)",ev["issueCategory"] == POTHOLE)
            record("verificationType == AUTO(0)",ev["verificationType"] == AUTO)
            record("aiScore correct",            ev["aiScore"] == ai_score)
            record("finalScore correct",         ev["finalScore"] == final_score)
            record("timestamp > 0",              ev["timestamp"] > 0)

    except Exception as e:
        record("registerComplaint() call", False, str(e))

    # ── TEST 2: getComplaint read-back ────────────────────────────────────────
    print(f"\n{B}{Y}[TEST 2] getComplaint() — on-chain state{Z}")
    try:
        c = contract.functions.getComplaint(complaint_id).call()
        print(f"\n  {B}📖 Stored struct:{Z}")
        print(f"    status           = {c[7]}  (0=VERIFIED, 1=RESOLVED)")
        print(f"    resolvedAt       = {c[4]}  (0 = not resolved yet)")
        print(f"    aiScore          = {c[8]}")
        print(f"    finalScore       = {c[9]}")
        print(f"    exists           = {c[10]}\n")

        record("exists == True",          c[10])
        record("status == VERIFIED (0)",  c[7] == 0)
        record("resolvedAt == 0",         c[4] == 0)
        record("aiScore stored",          c[8] == ai_score)
    except Exception as e:
        record("getComplaint()", False, str(e))

    # ── TEST 3: markResolved → ComplaintResolved ──────────────────────────────
    note = "Pothole filled — Municipal Corp Lahore"
    print(f"\n{B}{Y}[TEST 3] markResolved() → ComplaintResolved event{Z}")
    try:
        rec2 = send_tx(
            w3, account,
            contract.functions.markResolved(complaint_id, note),
            gas=200_000,
        )

        record("Transaction status == 1", rec2.status == 1,
               f"TX: 0x{rec2.transactionHash.hex()}")

        evs2 = contract.events.ComplaintResolved().process_receipt(rec2)
        record("ComplaintResolved event emitted", len(evs2) > 0,
               f"count: {len(evs2)}")

        if evs2:
            ev2 = evs2[0]["args"]
            print(f"\n  {B}📡 ComplaintResolved args:{Z}")
            print(f"    complaintId    = {ev2['complaintId']}")
            print(f"    timestamp      = {ev2['timestamp']}")
            print(f"    resolutionNote = {ev2['resolutionNote']}")
            print(f"    blockNumber    = {rec2.blockNumber}\n")

            record("complaintId correct",    ev2["complaintId"] == complaint_id)
            record("resolutionNote correct", ev2["resolutionNote"] == note)
            record("timestamp > 0",          ev2["timestamp"] > 0)

    except Exception as e:
        record("markResolved() call", False, str(e))

    # ── TEST 4: post-resolve state ────────────────────────────────────────────
    print(f"\n{B}{Y}[TEST 4] Post-resolution state{Z}")
    try:
        c2    = contract.functions.getComplaint(complaint_id).call()
        stats = contract.functions.getStats().call()

        print(f"\n  {B}📖 Updated struct:{Z}")
        print(f"    status     = {c2[7]}  (should be 1=RESOLVED)")
        print(f"    resolvedAt = {c2[4]}")
        print(f"\n  {B}📊 Stats:{Z}")
        print(f"    total={stats[0]}  resolved={stats[1]}  pending={stats[2]}\n")

        record("status == RESOLVED (1)",  c2[7] == 1)
        record("resolvedAt > 0",          c2[4] > 0)
        record("totalResolved >= 1",      stats[1] >= 1)
    except Exception as e:
        record("Post-resolve check", False, str(e))

    # ── TEST 5: duplicate revert guard ────────────────────────────────────────
    print(f"\n{B}{Y}[TEST 5] Duplicate registration → must revert{Z}")
    try:
        send_tx(
            w3, account,
            contract.functions.registerComplaint(
                complaint_id, image_hash_b32, POTHOLE,
                loc_hash_b32, AUTO, ai_score, final_score,
            ),
            gas=300_000,
        )
        record("Contract reverted on duplicate", False,
               "Tx SUCCEEDED — should have reverted! BUG 🐛")
    except Exception as e:
        is_rev = any(k in str(e).lower()
                     for k in ("revert","already registered","execution reverted"))
        record("Contract reverted (expected)", is_rev, str(e)[:100])

    # ── TEST 6: tamper detection ──────────────────────────────────────────────
    print(f"\n{B}{Y}[TEST 6] verifyImageHash() — tamper detection{Z}")
    try:
        ok_  = contract.functions.verifyImageHash(complaint_id, image_hash_b32).call()
        bad_ = contract.functions.verifyImageHash(complaint_id, bytes(32)).call()
        record("Correct hash → True",  ok_  == True)
        record("Wrong hash   → False", bad_ == False)
    except Exception as e:
        record("verifyImageHash()", False, str(e))

    # ── Summary ───────────────────────────────────────────────────────────────
    passed = sum(r["passed"] for r in results)
    failed = len(results) - passed

    print(f"\n{B}{C}{'='*60}{Z}")
    print(f"{B}  SUMMARY  —  {passed}/{len(results)} passed{Z}")
    print(f"{B}{C}{'='*60}{Z}")
    if failed:
        print(f"\n{R}Failed:{Z}")
        for r in results:
            if not r["passed"]:
                print(f"  ✗ {r['name']}")
                if r["detail"]: print(f"    {r['detail']}")
    print()
    if failed == 0:
        print(f"{G}{B}  🎉 All {len(results)} tests passed! Events emitting correctly.{Z}")
    else:
        print(f"{R}{B}  ⚠️  {failed} test(s) failed.{Z}")
    print(f"{B}{'='*60}{Z}\n")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)