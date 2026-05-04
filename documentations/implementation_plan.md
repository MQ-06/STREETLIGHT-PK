# StreetLight-PK — Full System Testing Plan

> **Goal**: Spin up every component, then execute an end-to-end functional test flow that exercises the complete complaint lifecycle — from citizen signup through AI validation, admin review, blockchain recording, and resolution.

---

## System Architecture Overview

| Component | Tech | Location | Port |
|-----------|------|----------|------|
| **Backend API** | FastAPI + SQLAlchemy + Supabase PostgreSQL | `backend/` | `8000` |
| **Blockchain** | Hardhat local node + Solidity contract | `blockchain-layer/` | `8545` |
| **Admin Dashboard** | React (Vite) + TailwindCSS | `municipal-admin/` | `5173` |
| **Mobile App** | Flutter | `frontend/` | N/A (emulator/device) |
| **AI Layers** | PyTorch + OpenCV (L0–L5 pipeline) | `backend/ai_layers/` | In-process |

---

## Phase 0 — Startup Sequence

> [!IMPORTANT]
> All 4 services must be running simultaneously in separate terminals. Start them in the order below.

### Step 0.1 — Blockchain (Hardhat Local Node)

```powershell
cd blockchain-layer
npm install                          # first time only
npx hardhat compile                  # compile streetLight.sol → ABI
npx hardhat node                     # starts JSON-RPC at 127.0.0.1:8545
```

Then in a **second terminal** deploy the contract:

```powershell
cd blockchain-layer
npx hardhat run scripts/deploy.js --network localhost
```

**Expected Result**:
- Console prints `✅ StreetLight deployed successfully!`
- Prints `📍 Contract Address: 0x...` — **copy this address**

> [!NOTE]
> After deployment, add these to `backend/.env`:
> ```
> BLOCKCHAIN_ENABLED=true
> BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
> CONTRACT_ADDRESS=<the address from deploy>
> DEPLOYER_PRIVATE_KEY=<account #0 private key from hardhat node output>
> ```

---

### Step 0.2 — Backend API

```powershell
cd backend
pip install -r requirements.txt      # first time only
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Result** (console logs):
```
🚦 STREETLIGHT BACKEND STARTING
✓ Database schema ensured
✓ Layer 0 (Input Validation) initialized
✓ Found model file: best_model.pth in models/
✓ Layer 1 (AI Engine) initialized successfully
✓ Image storage initialized
✅ STREETLIGHT BACKEND READY
🤖 Agent Scheduler Started
```

> [!WARNING]
> If you see `⚠️ Layer 1 DISABLED — server running in fallback mode`, the `best_model.pth` file is missing or corrupt. The system will still work but all reports get a fallback score of 50/100 and require manual officer review.

---

### Step 0.3 — Admin Dashboard

```powershell
cd municipal-admin
npm install                          # first time only
```
Create `.env` from `.env.example`:
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```
Then start:
```powershell
npm run dev
```

**Expected Result**: Vite prints `Local: http://localhost:5173/`

---

### Step 0.4 — Flutter App

```powershell
cd frontend
flutter pub get                      # first time only
flutter run                          # or flutter run -d <device>
```

**Expected Result**: App launches on emulator/device with the StreetLight splash screen.

---

## Phase 1 — Health Check Tests

### Test 1.1 — Backend Health

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `GET http://127.0.0.1:8000/` | `{"message": "StreetLight Backend Running", "version": "1.0.0", "ai_agent": "operational"}` |
| 2 | `GET http://127.0.0.1:8000/health` | `{"status": "healthy", "service": "streetlight-api", "ai_agent": "operational"}` |

### Test 1.2 — Database Connection

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Backend starts without DB errors | `✓ Database schema ensured` in console |
| 2 | Any authenticated API call succeeds | Confirms Supabase PostgreSQL is reachable |

### Test 1.3 — Blockchain Health

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Hardhat node console shows `Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545` | Node running |
| 2 | Backend logs `✅ BlockchainService fully initialized` | Contract loaded and connected |

---

## Phase 2 — Citizen Flow (Flutter App / API)

### Test 2.1 — Citizen Signup

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `POST /signup` with body: `{"first_name": "Test", "last_name": "User", "cnic": "12345-1234567-1", "email": "test@test.com", "password": "Test@1234"}` | `{"message": "User created successfully", "user_id": <int>}` |
| 2 | Repeat same CNIC | `400: CNIC already registered` |
| 3 | Repeat same email | `400: Email already registered` |

### Test 2.2 — Citizen Login

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `POST /login` with `{"email": "test@test.com", "password": "Test@1234"}` | `{"access_token": "<jwt>", "token_type": "bearer", "user": {...}}` |
| 2 | Wrong password | `401: Invalid email or password` |
| 3 | Save the `access_token` — used as `Authorization: Bearer <token>` for all subsequent calls | JWT contains `user_id`, `email`, `role` |

---

## Phase 3 — AI-Powered Report Creation (Core Flow)

> This is the most critical test — exercises Layers 0 through 5 + Cloudinary + DB.

### Test 3.1 — Submit a Valid Pothole Report

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `POST /reports/create` as **multipart/form-data** with: `image` = clear photo of a pothole, `title` = "Civic Issue on Main Road", `location_address` = "Main Road, Islamabad", `location_city` = "Islamabad", `location_lat` = 33.6844, `location_lng` = 73.0479 | See expected response below |

**Expected Response** (success):
```json
{
  "success": true,
  "merged": false,
  "message": "Pothole detected with high confidence...",
  "report": {
    "id": <int>,
    "issue_category": "POTHOLE",
    "status": "PENDING",
    "kanban_stage": "VERIFIED",
    ...
  },
  "ai_results": {
    "confidence": 85.5,         // varies — must be ≥ 68
    "severity": "medium",       // small | medium | large
    "final_score": 78.3,        // must be ≥ 60 to pass
    "gps_verification": {
      "status": "no_gps_in_photo", // or "verified"
      "is_spoofed": false
    }
  },
  "validation": {
    "quality_score": 72.0,      // Layer 0 image quality
    "warnings": [...]
  },
  "fraud_check": {
    "is_flagged_for_spam": false,
    "is_duplicate": false
  },
  "community_verification": {
    "status": "PENDING",
    "request_created": true
  },
  "routing": {
    "success": true,            // if routing table has Islamabad entry
    "city": "Islamabad",
    "department": "Roads"
  }
}
```

### Test 3.2 — Submit a Blurry/Invalid Image

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Submit a very blurry or dark photo | `400` with `agent_decision: "REJECTED"`, `error_code: "VALIDATION_FAILED"` |
| 2 | Check `errors` array | Contains specific reason like "Image too blurry" or "Image too dark" |

### Test 3.3 — Submit Non-Civic Image (e.g. selfie, food)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Submit a random photo (cat, selfie, etc.) | `400` with `error_code: "UNKNOWN_ISSUE_TYPE"` or `"LOW_AI_CONFIDENCE"` |
| 2 | AI detected class should be `"other"` with low confidence | Report **not** saved to DB |

### Test 3.4 — Submit Without GPS

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Omit `location_lat` and `location_lng` | `400: GPS coordinates are required` |

### Test 3.5 — Duplicate Detection

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Submit the **exact same image** from Test 3.1 again, same user | Response contains `"merged": true, "message": "...merged with an existing report..."` |
| 2 | Original report's `confirmation_count` increments | Check via `GET /reports/feed` |

---

## Phase 4 — Report Feed & Interactions

### Test 4.1 — Get Feed

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `GET /reports/feed?skip=0&limit=20` | Returns list of reports including the one from Test 3.1 |
| 2 | Check report fields | `id`, `image_url`, `issue_category`, `status`, `support_count`, `verify_count` all present |

### Test 4.2 — Support / Verify Interactions

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `POST /reports/{id}/support` | `support_count` increments by 1 |
| 2 | Repeat same call | Should either toggle or return "already supported" |
| 3 | `POST /reports/{id}/verify` | `verify_count` increments by 1 |

---

## Phase 5 — Community Verification (Layer 3)

### Test 5.1 — Get Pending Verifications

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `GET /verification/pending?lat=33.6844&lng=73.0479` (with **different user** than reporter) | Returns verification request for the report from Test 3.1 |
| 2 | Response includes `request_id`, `report_id`, `distance_m` | Distance should be ≈ 0m if same GPS |

### Test 5.2 — Submit Vote

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `POST /verification/{request_id}/vote` with `{"vote": "YES"}` | `{"success": true, "message": "Vote recorded"}` |
| 2 | Impact score of voter increases | Check via user profile endpoint |

---

## Phase 6 — Admin Dashboard Tests

### Test 6.1 — Admin Login

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open `http://localhost:5173/signin` | Sign-in page renders |
| 2 | Login with **super_admin** credentials | Redirects to `/dashboard` |
| 3 | Login with **city_admin** credentials | Redirects to `/dashboard` (city-scoped view) |
| 4 | Login with **dept_officer** credentials | Redirects to `/dashboard` (dept-scoped view) |
| 5 | Login with citizen credentials | `403: Access denied. Admin dashboard role required.` |

### Test 6.2 — Dashboard Overview

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Dashboard loads without errors | KPI cards show total reports, resolved, pending counts |
| 2 | Recent complaints table populated | Shows report from Test 3.1 |
| 3 | Kanban counts visible | At least 1 report in VERIFIED column |

### Test 6.3 — Complaint Management

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to `/complaint-management` | Table loads with all reports |
| 2 | Click a report row | Navigates to `/complaint-detail/:id` |
| 3 | Detail page shows AI results, GPS info, image | All fields populated |

### Test 6.4 — Resolution Board (Kanban)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to `/resolution-board` | Kanban columns render (NEW → VERIFIED → IN_PROGRESS → RESOLVED → CLOSED) |
| 2 | Drag report card from VERIFIED to IN_PROGRESS | `PATCH /admin/reports/{id}/stage` fires, card moves |
| 3 | Refresh page | Card remains in new position |

### Test 6.5 — Hotspot Map

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to `/hotspot-map` | Map renders with report pins at GPS coordinates |
| 2 | Click a pin | Detail panel opens showing report info |
| 3 | Filter by category (POTHOLE) | Only pothole pins shown |

### Test 6.6 — Analytics

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to `/analytics` | Charts and KPIs render |
| 2 | Change time range (7/30/90 days) | Charts update with new data range |
| 3 | Super admin sees national view | City breakdown visible |

### Test 6.7 — Organization (Super Admin / City Admin only)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to `/organization` | Departments tab loads with routing table entries |
| 2 | Users tab shows admin users | Can create/update officers |
| 3 | Dept officer tries to access | Redirected to `/dashboard` |

---

## Phase 7 — Resolution Lifecycle (End-to-End)

> This tests the complete resolution flow from officer → citizen → blockchain.

### Test 7.1 — Officer Marks Resolved

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | In Kanban, drag report to RESOLVED (or upload after-image via detail page) | Report status → RESOLVED |
| 2 | `after_image_url` populated | Cloudinary URL stored |
| 3 | `kanban_stage` → AWAITING_FEEDBACK or RESOLVED | Depends on workflow path |

### Test 7.2 — Citizen Confirms Resolution (Mobile)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Citizen receives notification (FCM if configured) | Or poll resolution endpoint |
| 2 | `POST /reports/resolution/confirm` with `{"report_id": <id>, "response": "CONFIRMED"}` | Report moves to CLOSED |
| 3 | `citizen_response` = "CONFIRMED", `closed_at` populated | DB fields updated |

### Test 7.3 — Auto-Close (Timeout)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | If citizen doesn't respond within `AUTO_CLOSE_DAYS` (7 days) | Agent auto-closes the report |
| 2 | Trigger manually via `GET /test-agent` (super_admin only) | `check_auto_close` runs |

---

## Phase 8 — Blockchain Integration

### Test 8.1 — Complaint Registered On-Chain

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | After a report reaches VERIFIED status with score ≥ 85 (auto) or officer approval (60–84) | Backend calls `registerComplaint()` |
| 2 | Check backend logs | `⛓️ BLOCKCHAIN: Registering complaint #<id>` with TX hash |
| 3 | Hardhat node console | Shows transaction confirmation |

### Test 8.2 — Read Complaint Proof

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `GET /blockchain/proof/{complaint_id}` (if endpoint exists) or call `getComplaint()` directly | Returns on-chain data: `imageHash`, `aiScore`, `finalScore`, `status: VERIFIED` |
| 2 | Verify `imageHash` matches the SHA256 of the original image URL | Tamper-proof verification |

### Test 8.3 — Blockchain Stats

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call `getStats()` on contract | Returns `total`, `resolved`, `pending` counts |
| 2 | Counts match what was registered | `total` ≥ 1 after Test 8.1 |

---

## Phase 9 — Agent Scheduler

### Test 9.1 — Manual Agent Trigger

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `GET /test-agent` with super_admin JWT | `{"message": "Agent cycle completed"}` |
| 2 | Check backend logs | `🔄 Agent cycle started`, `📦 Found X active reports`, `✅ Agent cycle completed` |
| 3 | Reports in PENDING with high scores may auto-verify | `kanban_stage` transitions happen |

### Test 9.2 — Automatic 15-min Cycle

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Wait 15 minutes after backend startup | Agent cycle runs automatically |
| 2 | Check backend logs | Same output as 9.1 |

---

## Phase 10 — Edge Cases & Error Handling

| Test | Action | Expected Result |
|------|--------|-----------------|
| 10.1 | Submit report with no auth token | `401 Unauthorized` |
| 10.2 | Admin login with expired JWT | `401` on any admin endpoint |
| 10.3 | Access admin endpoint with citizen role | `403 Forbidden` |
| 10.4 | Submit report with GPS outside Pakistan | May still work but routing might fail (no matching city) |
| 10.5 | Submit 10+ reports in 1 hour (same user) | Spam flag set: `is_flagged_for_spam: true`, impact penalty applied |
| 10.6 | Blockchain disabled in .env | Backend runs fine with `⚠️ Blockchain DISABLED` warning, all blockchain calls return `skipped: true` |

---

## Open Questions

> [!IMPORTANT]
> **Test Accounts**: Do you already have admin accounts (super_admin, city_admin, dept_officer) in the database, or do I need to create them via SQL/seed script?

> [!IMPORTANT]
> **Flutter Testing**: Do you want me to test the Flutter app via the emulator, or is API-level testing (via curl/Swagger) sufficient for now?

> [!IMPORTANT]
> **Blockchain Node Modules**: Does `blockchain-layer/` already have `node_modules` installed, or should I run `npm install` first?

---

## Verification Plan

### Automated Tests
1. Start backend → hit `/health` and `/` endpoints
2. Run `GET /test-agent` to validate agent cycle
3. Verify Swagger docs at `http://127.0.0.1:8000/docs`

### Manual Verification
1. Walk through the full report lifecycle via API (Phases 2–8)
2. Verify admin dashboard visually in browser (Phase 6)
3. Check Hardhat console for blockchain transactions (Phase 8)
4. Cross-check database state via Supabase dashboard after each phase
