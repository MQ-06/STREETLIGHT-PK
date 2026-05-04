# StreetLight-PK — Complete Testing Documentation

> **Version**: 1.0  
> **Date**: 2026-05-04  
> **Branch**: `test`  
> **Test Log File**: `documentations/test_log.md`

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Complaint Routing & Email Accounts](#2-complaint-routing--email-accounts)
3. [Test Accounts](#3-test-accounts)
4. [Startup Sequence](#4-startup-sequence)
5. [Test Phases](#5-test-phases)
   - Phase 1: Health Checks
   - Phase 2: Citizen Signup & Login
   - Phase 3: AI-Powered Report Creation
   - Phase 4: Report Feed & Interactions
   - Phase 5: Community Verification (Layer 3)
   - Phase 6: Admin Dashboard UI/UX
   - Phase 7: Status Mirroring Across All Components
   - Phase 8: Notification Pipeline (Every Status Change)
   - Phase 9: Resolution Lifecycle (End-to-End)
   - Phase 10: Blockchain Integration
   - Phase 11: Agent Scheduler
   - Phase 12: UI/UX Functional Verification & Fixes
   - Phase 13: Edge Cases & Error Handling
6. [Git Workflow](#6-git-workflow)
7. [Test Log Template](#7-test-log-template)
8. [Test Summary](#8-test-summary)

---

## 1. System Overview

| Component | Tech | Location | Port |
|-----------|------|----------|------|
| **Backend API** | FastAPI + SQLAlchemy + Supabase PostgreSQL | `backend/` | `8000` |
| **Blockchain** | Hardhat local node + Solidity contract | `blockchain-layer/` | `8545` |
| **Admin Dashboard** | React (Vite) + TailwindCSS | `municipal-admin/` | `5173` |
| **Mobile App** | Flutter (installed on phone) | `frontend/` | N/A |
| **AI Layers** | PyTorch + OpenCV (L0–L5 pipeline) | `backend/ai_layers/` | In-process |

### Complete Report Lifecycle (Status Flow)

```
CITIZEN SUBMITS REPORT
  → AI Layer 0 (Image Validation) → Layer 1 (Classification) → Layer 2 (Fraud)
  → Layer 3 (Community Verification) → Layer 4 (Trust) → Layer 5 (Final Score)
  → Auto-Routing (GPS → City → Department → Officer)
  → Email Notification to Officer

STATUS FLOW:
  PENDING → VERIFIED → IN_PROGRESS → AWAITING_FEEDBACK → RESOLVED → CLOSED

KANBAN FLOW:
  NEW → PENDING_VERIFICATION → VERIFIED → IN_PROGRESS → AWAITING_FEEDBACK → RESOLVED → CLOSED

AT EACH STAGE:
  ✓ Database updated
  ✓ Dashboard reflects change (Kanban, tables, analytics)
  ✓ Citizen notified (FCM push / in-app)
  ✓ Blockchain entry (at VERIFIED + CLOSED)
  ✓ Audit log entry written
```

---

## 2. Complaint Routing & Email Accounts

When a citizen submits a report, the system auto-routes based on **GPS city detection + AI classification**:

```
Photo → AI Classification (pothole/garbage)
  → GPS → City (Lahore/Faisalabad)
    → Department (LMC/LWMC/FMC/FWMC)
      → Officer assigned from routing_table
        → Email notification sent to officer's notification_email
```

### Routing Table

| City | Issue Type | Dept Code | Department Full Name | Officer | Notification Email |
|------|-----------|-----------|---------------------|---------|-------------------|
| Lahore | Pothole | `lmc` | Lahore Metropolitan Corporation | Ahmad Raza | `bitf22m006@pucit.edu.pk` |
| Lahore | Garbage | `lwmc` | Lahore Waste Management Company | Sara Khan | `bitf22m044@pucit.edu.pk` |
| Faisalabad | Pothole | `fmc` | Faisalabad Metropolitan Corporation | Bilal Chaudhry | `bitf22m011@pucit.edu.pk` |
| Faisalabad | Garbage | `fwmc` | Faisalabad Waste Management Company | Ayesha Nawaz | `bitf22m015@pucit.edu.pk` |

> **Note**: Email notifications require `SMTP_USER` and `SMTP_PASSWORD` (Gmail App Password) in `backend/.env`. Without these, emails are silently skipped but routing still works.

---

## 3. Test Accounts

**Password for ALL accounts: `Admin@123`**

Seed script: `backend/script/seed_routing_table.py`

### Admin Accounts (Dashboard Login)

| Email | Role | Scope | Can See |
|-------|------|-------|---------|
| `super_admin@streetlight.local` | `super_admin` | All Pakistan | Everything — all cities, departments |
| `lahore_ca@streetlight.local` | `city_admin` | Lahore | Only Lahore reports and officers |
| `faisalabad_ca@streetlight.local` | `city_admin` | Faisalabad | Only Faisalabad reports and officers |
| `ahmad.raza@streetlight.local` | `dept_officer` | Lahore / LMC | Only Lahore pothole reports |
| `sara.khan@streetlight.local` | `dept_officer` | Lahore / LWMC | Only Lahore garbage reports |
| `bilal.chaudhry@streetlight.local` | `dept_officer` | Faisalabad / FMC | Only Faisalabad pothole reports |
| `ayesha.nawaz@streetlight.local` | `dept_officer` | Faisalabad / FWMC | Only Faisalabad garbage reports |

### Citizen Accounts (Flutter App)

Any user registered via `/signup` or Flutter registration screen (default role: `citizen`).

---

## 4. Startup Sequence

> **Start services in this order. All must run simultaneously in separate terminals.**

### 4.1 — Blockchain (Hardhat Local Node)

```powershell
cd blockchain-layer
npm install                              # first time only
npx hardhat compile                      # compile streetLight.sol → ABI
npx hardhat node                         # starts at 127.0.0.1:8545
```

In a **second terminal** deploy:

```powershell
cd blockchain-layer
npx hardhat run scripts/deploy.js --network localhost
```

**Expected**: `✅ StreetLight deployed successfully!` + `📍 Contract Address: 0x...`

After deploy, add to `backend/.env`:
```env
BLOCKCHAIN_ENABLED=true
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=<address from deploy output>
DEPLOYER_PRIVATE_KEY=<account #0 private key from hardhat node>
```

### 4.2 — Backend API

```powershell
cd backend
pip install -r requirements.txt          # first time only
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected console logs**: `✅ STREETLIGHT BACKEND READY` + `🤖 Agent Scheduler Started`

### 4.3 — Admin Dashboard

```powershell
cd municipal-admin
npm install                              # first time only
# Create .env: VITE_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```

**Expected**: `Local: http://localhost:5173/`

### 4.4 — Flutter App

Install on phone via USB: `flutter run` or build APK.

---

## 5. Test Phases

---

### PHASE 1 — Health Checks

| ID | Action | Expected Result |
|----|--------|-----------------|
| 1.1 | `GET http://127.0.0.1:8000/` | `{"message": "StreetLight Backend Running", "version": "1.0.0"}` |
| 1.2 | `GET http://127.0.0.1:8000/health` | `{"status": "healthy"}` |
| 1.3 | `GET http://127.0.0.1:8000/docs` | Swagger UI loads with all endpoints |
| 1.4 | Backend console has no errors | `✓ Database schema ensured` present |
| 1.5 | Hardhat node running | `Started HTTP ... at http://127.0.0.1:8545` |
| 1.6 | `http://localhost:5173/signin` | Dashboard sign-in page renders |

---

### PHASE 2 — Citizen Signup & Login

| ID | Action | Expected Result |
|----|--------|-----------------|
| 2.1 | `POST /signup` — new citizen | `{"message": "User created successfully", "user_id": <int>}` |
| 2.2 | Repeat same CNIC | `400: CNIC already registered` |
| 2.3 | Repeat same email | `400: Email already registered` |
| 2.4 | `POST /login` — correct credentials | `{"access_token": "<JWT>", "user": {"role": "citizen"}}` |
| 2.5 | `POST /login` — wrong password | `401: Invalid email or password` |
| 2.6 | `POST /login` — non-existent email | `401: Invalid email or password` |

---

### PHASE 3 — AI-Powered Report Creation

| ID | Action | Expected Result |
|----|--------|-----------------|
| 3.1 | Submit valid pothole photo (Lahore GPS: 31.5204, 74.3587) | `success: true`, `issue_category: "POTHOLE"`, routed to Ahmad Raza |
| 3.2 | Verify routing email | `bitf22m006@pucit.edu.pk` received notification (or log shows `✅ Email sent`) |
| 3.3 | Verify Cloudinary upload | `report.image_url` starts with `https://res.cloudinary.com/` |
| 3.4 | Submit valid garbage photo (Faisalabad GPS: 31.4187, 73.0791) | `issue_category: "TRASH"`, routed to Ayesha Nawaz |
| 3.5 | Submit very blurry/dark photo | `400`, `error_code: "VALIDATION_FAILED"` |
| 3.6 | Submit non-civic image (selfie/cat/food) | `400`, `error_code: "UNKNOWN_ISSUE_TYPE"` |
| 3.7 | Submit without GPS (omit lat/lng) | `400: GPS coordinates are required` |
| 3.8 | Submit without auth token | `401 Unauthorized` |
| 3.9 | Submit exact same image again | `merged: true` — merged into original report |
| 3.10 | Original report `confirmation_count` incremented | Check via `GET /reports/feed` |

---

### PHASE 4 — Report Feed & Interactions

| ID | Action | Expected Result |
|----|--------|-----------------|
| 4.1 | `GET /reports/feed?skip=0&limit=20` | Returns reports from Phase 3 |
| 4.2 | Report fields present | `id`, `image_url`, `issue_category`, `status`, `support_count`, `views` |
| 4.3 | `POST /reports/<id>/support` | `support_count` +1 |
| 4.4 | `POST /reports/<id>/verify` | `verify_count` +1 |
| 4.5 | Category filter: `GET /reports/feed?category=POTHOLE` | Only pothole reports returned |

---

### PHASE 5 — Community Verification (Layer 3)

| ID | Action | Expected Result |
|----|--------|-----------------|
| 5.1 | Create 2nd citizen + login | New JWT token |
| 5.2 | `GET /verification/pending?lat=31.5204&lng=74.3587` (2nd user) | Returns pending verification for report from 3.1 |
| 5.3 | `POST /verification/<request_id>/vote` — `{"vote": "YES"}` | `success: true, message: "Vote recorded"` |
| 5.4 | Voter impact score increased | Check profile endpoint |
| 5.5 | `GET /verification/<report_id>/status` | Shows vote tally and status |
| 5.6 | Reporter can't verify own report | Own reports excluded from pending list |

---

### PHASE 6 — Admin Dashboard UI/UX

| ID | Action | Expected Result |
|----|--------|-----------------|
| 6.1 | Login as `super_admin@streetlight.local` | Redirects to `/dashboard` |
| 6.2 | Login as `lahore_ca@streetlight.local` | City-scoped dashboard |
| 6.3 | Login as `ahmad.raza@streetlight.local` | Dept-scoped dashboard |
| 6.4 | Login with citizen account | `403: Access denied` |
| 6.5 | Dashboard KPI cards load | Total, Resolved, Pending counts |
| 6.6 | Recent complaints table populated | Shows reports |
| 6.7 | Navigate `/complaint-management` | Table loads |
| 6.8 | Click report row → detail page | Shows AI results, GPS, image |
| 6.9 | Navigate `/resolution-board` | Kanban columns render |
| 6.10 | Drag card VERIFIED → IN_PROGRESS | Card moves, API fires |
| 6.11 | Refresh — card stays in position | Persisted correctly |
| 6.12 | Navigate `/hotspot-map` | Map renders with pins |
| 6.13 | Click pin → detail panel | Report info shown |
| 6.14 | Navigate `/analytics` | Charts and KPIs render |
| 6.15 | Change time range (7/30/90 days) | Charts update |
| 6.16 | Navigate `/organization` (super_admin) | Routing table + users tabs |
| 6.17 | `/organization` as dept_officer | Redirected to `/dashboard` |
| 6.18 | Navigate `/audit-log` | Audit entries load |
| 6.19 | Navigate `/transparency` | KPI data loads |
| 6.20 | Sign out → redirects to `/signin` | Token cleared |

---

### PHASE 7 — Status Mirroring Across All Components ⭐

> **Critical**: When status changes in ONE component, ALL components must reflect it.

#### 7A — Status Change: VERIFIED → IN_PROGRESS (Admin Dashboard)

| ID | Action | Check Component | Expected Result |
|----|--------|-----------------|-----------------|
| 7.1 | Drag card to IN_PROGRESS in Kanban | **Dashboard** | Card in IN_PROGRESS column |
| 7.2 | | **Database** (Supabase) | `kanban_stage = IN_PROGRESS`, `status = IN_PROGRESS` |
| 7.3 | | **Flutter App** (feed refresh) | Report shows `status: IN_PROGRESS` |
| 7.4 | | **Audit Log** (dashboard) | Log entry: stage change VERIFIED → IN_PROGRESS |

#### 7B — Status Change: IN_PROGRESS → AWAITING_FEEDBACK (After-image Upload)

| ID | Action | Check Component | Expected Result |
|----|--------|-----------------|-----------------|
| 7.5 | Officer uploads after-image via complaint detail | **Dashboard** | After-image visible, stage = AWAITING_FEEDBACK |
| 7.6 | | **Database** | `after_image_url` populated, `kanban_stage = AWAITING_FEEDBACK` |
| 7.7 | | **Flutter App** | Citizen sees notification to confirm resolution |
| 7.8 | | **Audit Log** | Log entry with after-image upload + stage change |

#### 7C — Status Change: AWAITING_FEEDBACK → RESOLVED → CLOSED (Citizen Confirms)

| ID | Action | Check Component | Expected Result |
|----|--------|-----------------|-----------------|
| 7.9 | Citizen confirms resolution in Flutter app | **Database** | `citizen_response = CONFIRMED`, `status = CLOSED`, `closed_at` set |
| 7.10 | | **Dashboard** (Kanban) | Card in CLOSED column |
| 7.11 | | **Dashboard** (Analytics) | Resolved count incremented |
| 7.12 | | **Blockchain** | `markResolved()` called — TX hash stored in `blockchain_resolve_tx` |
| 7.13 | | **Hardhat Console** | Transaction confirmed |
| 7.14 | | **Flutter App** | Report shows CLOSED status |
| 7.15 | | **Audit Log** | 2 entries: RESOLVED + CLOSED with blockchain TX |

#### 7D — Status Change: Citizen REJECTS Resolution

| ID | Action | Check Component | Expected Result |
|----|--------|-----------------|-----------------|
| 7.16 | Citizen rejects resolution in Flutter | **Database** | `citizen_response = REJECTED`, `kanban_stage = IN_PROGRESS` |
| 7.17 | | **Dashboard** (Kanban) | Card moved back to IN_PROGRESS |
| 7.18 | | **Officer** (push notification) | Gets "Citizen rejected resolution ❌" push |
| 7.19 | | **After-image** cleared | `after_image_url = NULL` |
| 7.20 | | **Audit Log** | Log entry: AWAITING_FEEDBACK → IN_PROGRESS with rejection note |

#### 7E — RESOLVED Without After-Image (Agent Catches)

| ID | Action | Check Component | Expected Result |
|----|--------|-----------------|-----------------|
| 7.21 | Try to resolve without after-image | **Agent** | Reverts to IN_PROGRESS automatically |
| 7.22 | | **Officer** | Gets "After-image required ⚠️" push |
| 7.23 | | **Database** | `kanban_stage = IN_PROGRESS` |
| 7.24 | | **Audit Log** | "RESOLVED attempted but no after-image uploaded" |

---

### PHASE 8 — Notification Pipeline (Every Status Change) ⭐

> **Critical**: Citizen must be notified at each meaningful status change.

| ID | Status Change | Notification Type | Recipient | Expected |
|----|--------------|-------------------|-----------|----------|
| 8.1 | Report created + routed | In-app + push (FCM) | **Citizen** (reporter) | "Your report has been routed to [DEPT] in [CITY]" |
| 8.2 | Report created + routed | Email notification | **Officer** (assigned) | Email to `notification_email` with report details |
| 8.3 | Officer uploads after-image | In-app + push (FCM) | **Citizen** | "Your issue has been fixed! ✅ Please confirm" |
| 8.4 | Citizen rejects resolution | Push (FCM) | **Officer** | "Citizen rejected resolution ❌" |
| 8.5 | Resolution finalized (CLOSED) | Push (FCM) | **Citizen** | "Complaint Closed ✅ Thank you!" |
| 8.6 | After-image fails verification | Push (FCM) | **Officer** | "After-image rejected ❌ Please re-upload" |
| 8.7 | Agent auto-closes (7 days timeout) | Push (FCM) | **Citizen** | "Complaint Closed ✅" |
| 8.8 | Report verified by community votes | In-app | **Citizen** | Status updated to VERIFIED |

> **Verify**: Check backend logs for `📱 Citizen ... resolution prompt`, `✅ Email sent →`, `FCM=sent/skipped`

---

### PHASE 9 — Resolution Lifecycle (Full End-to-End)

| ID | Action | Expected Result |
|----|--------|-----------------|
| 9.1 | Create report via Flutter app (Lahore pothole) | Report created, routed to Ahmad Raza |
| 9.2 | Login as `ahmad.raza@streetlight.local` in dashboard | See the report in complaint list |
| 9.3 | Move report to IN_PROGRESS in Kanban | Stage updated in DB + dashboard |
| 9.4 | Upload after-image via complaint detail page | `after_image_url` populated, stage → AWAITING_FEEDBACK |
| 9.5 | Citizen gets FCM/in-app notification | "Your issue has been fixed! Please confirm" |
| 9.6 | Citizen opens Flutter app → Resolution screen | Sees before/after images |
| 9.7 | Citizen taps "Confirm" | `POST /reports/resolution/confirm` → CONFIRMED |
| 9.8 | Report → RESOLVED → blockchain → CLOSED | Full finalization chain |
| 9.9 | Dashboard Kanban shows card in CLOSED | Mirrored |
| 9.10 | Database: `status=CLOSED`, `closed_at` set, `blockchain_resolve_tx` populated | All fields correct |
| 9.11 | Analytics: resolved count +1 | Dashboard analytics updated |
| 9.12 | Citizen gets final "Complaint Closed ✅" notification | Notification received |

---

### PHASE 10 — Blockchain Integration

| ID | Action | Expected Result |
|----|--------|-----------------|
| 10.1 | Report reaches VERIFIED (score ≥ 85 auto) | `registerComplaint()` called on-chain |
| 10.2 | Backend logs | `⛓️ BLOCKCHAIN: Registering complaint #<id>` + TX hash |
| 10.3 | Hardhat console | Transaction confirmed in block |
| 10.4 | Read on-chain proof: `getComplaint(<id>)` | Returns `imageHash`, `aiScore`, `finalScore`, `status: VERIFIED` |
| 10.5 | `getStats()` on contract | `total ≥ 1`, `pending ≥ 1` |
| 10.6 | Run `python script/test_blockchain.py` | Registers complaint #999 + reads proof |
| 10.7 | After CLOSED: `markResolved()` on-chain | `blockchain_resolve_tx` stored in DB |
| 10.8 | On-chain status changes to RESOLVED | `getComplaint()` shows `status: RESOLVED` |

---

### PHASE 11 — Agent Scheduler

| ID | Action | Expected Result |
|----|--------|-----------------|
| 11.1 | `GET /test-agent` (super_admin JWT) | `{"message": "Agent cycle completed"}` |
| 11.2 | Backend logs | `🔄 Agent cycle started` → `📦 Found X active reports` → `✅ completed` |
| 11.3 | Reports in PENDING with high scores | May auto-transition to VERIFIED |
| 11.4 | Wait 15 min after startup | Agent runs automatically |
| 11.5 | `GET /test-agent` (non-super_admin) | `403: Only super_admin may trigger` |
| 11.6 | Auto-close test: AWAITING_FEEDBACK > 7 days | `check_auto_close` finalizes the report |

---

### PHASE 12 — UI/UX Functional Verification & Fixes ⭐

> **Goal**: Verify every interactive UI element works. If something is broken (e.g. search bar), FIX it and commit.

#### Dashboard UI Elements

| ID | Element | Page | Test Action | Expected Result |
|----|---------|------|-------------|-----------------|
| 12.1 | Search bar (top nav) | All pages | Type query, press Enter | Filters reports by search term |
| 12.2 | Search in Complaint Management | `/complaint-management` | Type report ID or title | Table filters to matching reports |
| 12.3 | Search in Resolution Board | `/resolution-board` | Type query | Kanban filters cards |
| 12.4 | Search in User Roles | `/organization?tab=users` | Type officer name/email | List filters |
| 12.5 | Stage filter dropdown | `/complaint-management` | Select a stage | Only reports in that stage shown |
| 12.6 | Date range filter | `/complaint-management` | Select date range | Reports filtered by date |
| 12.7 | Clear filters button | `/complaint-management` | Click "Clear" | All filters reset |
| 12.8 | Category filter on map | `/hotspot-map` | Select POTHOLE only | Only pothole pins visible |
| 12.9 | Export CSV button | `/analytics` | Click export | CSV file downloads |
| 12.10 | PDF report modal | `/analytics` | Click generate report | PDF opens/downloads |
| 12.11 | Kanban drag-and-drop | `/resolution-board` | Drag card between columns | Card moves + API call fires |
| 12.12 | Pagination | `/complaint-management` | Click next page | New page of results loads |
| 12.13 | Responsive layout | All pages | Resize browser window | Layout adapts without breaking |
| 12.14 | Sign out button | Top nav | Click sign out | Token cleared, redirect to `/signin` |
| 12.15 | Profile page | `/my-profile` | Load page | Shows current admin user info |

#### Flutter App UI Elements

| ID | Element | Screen | Test Action | Expected Result |
|----|---------|--------|-------------|-----------------|
| 12.16 | Splash screen | Launch | Open app | Logo + loading animation |
| 12.17 | Login form validation | Login | Submit empty fields | Validation errors shown |
| 12.18 | Registration form | Registration | Fill all fields + submit | Account created |
| 12.19 | Report submission | Report Issue | Take photo, fill fields, submit | Report created with AI result |
| 12.20 | Feed infinite scroll | Home | Scroll down | More reports load |
| 12.21 | Support/Verify buttons | Report detail | Tap support | Count increments |
| 12.22 | Verification screen | Verification tab | View nearby pending requests | List loads within 2km |
| 12.23 | Resolution confirmation | Resolution screen | Confirm/Reject resolution | Status updates |
| 12.24 | Notification bell badge | Home | New notifications exist | Badge shows unread count |
| 12.25 | Profile screen | Profile tab | Load screen | Stats, impact score visible |

---

### PHASE 13 — Edge Cases & Error Handling

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| 13.1 | Submit report with no auth token | `401 Unauthorized` |
| 13.2 | Access admin API with citizen JWT | `403 Forbidden` |
| 13.3 | Admin login with expired JWT | `401` on API call |
| 13.4 | GPS outside Pakistan (e.g. 0, 0) | Report saves but routing fails: `kanban_stage = NEW` |
| 13.5 | 10+ reports in 1 hour (same user) | `is_flagged_for_spam: true`, penalty applied |
| 13.6 | `BLOCKCHAIN_ENABLED=false` | Backend runs; blockchain calls return `skipped: true` |
| 13.7 | AI model file missing | Fallback mode: `final_score = 50`, `agent_decision = "REVIEW"` |
| 13.8 | Invalid Kanban stage in PATCH | `400: Bad Request` |
| 13.9 | `dept_officer` views other city's reports | Empty list (scope filter) |
| 13.10 | Report in Islamabad (no routing entry) | Saved but not routed; `kanban_stage = NEW` |
| 13.11 | Double-vote on same verification | Error: already voted |
| 13.12 | Confirm resolution on non-AWAITING report | Error: "Report not awaiting feedback" |

---

## 6. Git Workflow

All testing work will be on a dedicated branch:

```powershell
# Create and switch to test branch
git checkout -b test

# After each test phase or fix:
git add .
git commit -m "test(phase-X): <description of what was tested/fixed>"

# Example commits:
# git commit -m "test(phase-1): verify health checks - all passed"
# git commit -m "fix(dashboard): search bar not filtering in complaint management"
# git commit -m "test(phase-7): status mirroring across all components verified"
# git commit -m "docs(test-log): add results for phases 1-6"

# Push to remote
git push origin test
```

### Commit Convention

```
test(phase-X): <what was tested>        — test result documentation
fix(component): <what was fixed>         — bug fix found during testing
docs(test-log): <what was documented>    — test log updates
```

---

## 7. Test Log Template

Every test case must be logged in `documentations/test_log.md` using this format:

```markdown
## Phase X — [Phase Name]

### Test X.Y — [Test Name]

| Field | Value |
|-------|-------|
| **Test ID** | X.Y |
| **Date** | YYYY-MM-DD HH:MM |
| **Tester** | [Name] |
| **Component** | Backend / Dashboard / Flutter / Blockchain |
| **Action Taken** | Exact steps performed |
| **Expected Result** | What should happen |
| **Actual Result** | What actually happened |
| **Status** | ✅ PASS / ❌ FAIL / ⚠️ PARTIAL |
| **Fix Applied** | (if FAIL) What was changed to fix it |
| **Commit** | (if fix) Commit hash + message |
| **Screenshots** | (if applicable) Path to screenshot |
| **Notes** | Any additional observations |
```

---

## 8. Test Summary

| Phase | Description | Total Tests | Passed | Failed | Fixed | Notes |
|-------|-------------|-----------|--------|--------|-------|-------|
| 1 | Health Checks | 6 | | | | |
| 2 | Citizen Signup & Login | 6 | | | | |
| 3 | AI Report Creation | 10 | | | | |
| 4 | Feed & Interactions | 5 | | | | |
| 5 | Community Verification | 6 | | | | |
| 6 | Admin Dashboard UI/UX | 20 | | | | |
| 7 | Status Mirroring | 24 | | | | |
| 8 | Notification Pipeline | 8 | | | | |
| 9 | Resolution Lifecycle | 12 | | | | |
| 10 | Blockchain Integration | 8 | | | | |
| 11 | Agent Scheduler | 6 | | | | |
| 12 | UI/UX Functional & Fixes | 25 | | | | |
| 13 | Edge Cases | 12 | | | | |
| **TOTAL** | | **148** | | | | |
