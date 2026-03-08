# Technical Implementation Logic: StreetLight AI Layers (2-5)

This document explains the internal mechanisms and orchestration of our report validation pipeline. Use this to understand the code flow for dashboard and blockchain integration.

---

## 🏗️ The Orchestration Pattern
**Location:** `backend/routers/flutter/mobile_auth.py` → `create_report()`

The backend follows a **Single-Entry Orchestration** pattern. A report is not just saved; it is passed through a "pipeline" of engine classes.

1.  **Pre-Persistence (Blocking):** Validations and fraud checks happen before the report is saved. If these fail, the transaction is rolled back or interrupted.
2.  **Persistence:** The report is committed to the DB.
3.  **Post-Persistence (Non-Blocking):** Heavy or optional layers (Community, Final Scoring) run after the user gets their response. Errors here are caught and logged but do not crash the request.

---

## 🐍 Engine Design Pattern
**Location:** `backend/ai_layers/`

All engines follow a consistent functional class pattern:
- **Initialization**: Takes a `db: Session`.
- **Public API**: A single entry method (e.g., `evaluate_trust()` or `calculate_final_score()`) that returns a flat dictionary.
- **Side Effects**: Engines are responsible for their own DB updates (e.g., updating the `combined_score` column on a report).
- **Logging**: Heavy use of emojis (`🔐`, `🎯`, `🏘️`) to make the console output readable during concurrent report processing.

---

## 🔍 Layer-Specific Implementation Logic

### Layer 2: Fraud Detection (`FraudEngine`)
- **Mechanism:** EXIF extraction. We use the `Pillow` library to extract GPS metadata from the uploaded image. We compare these coordinates using the **Haversine formula** against the coordinates reported by the user's phone.
- **Redundancy Logic:** Uses SQLAlchemy `.count()` queries to check for other reports with the same `IssueCategory` within a 5km radius and 24-hour window.

### Layer 3: Community Verification (`CommunityVerificationEngine`)
- **Spatial Discovery:** Uses a bounding box query (`lat +/- offset`, `lng +/- offset`) to find users whose `last_known_lat/lng` is within range.
- **Weighted Majority:** Instead of 1 user = 1 vote, we do `sum(voter.impact_score * vote_direction)`. This ensures veteran users carry more weight than new accounts.
- **Lazy Evaluation:** The `combined_score` (Step 5) is recalculated every time a new vote is cast (via the `/score/recalculate` trigger).

### Layer 4: Trust History (`TrustHistoryEngine`)
- **Feature Engineering:** It performs multiple sub-queries:
  1. `User` table for `created_at` (Account Age).
  2. `Report` table for frequency (Behavior).
  3. `UserProfile` for historical `fraud_flags`.
- **Normalization:** It maps raw values (e.g., `fraud_flags=2`) to a 0-100 scale using linear interpolation logic before weighting.

### Layer 5: Final Scoring (`FinalScoreCalculator`)
- **Weight Switching:** It uses conditional logic to detect if `community_score` is `None`. If so, it dynamically swaps the weights (45/55%) to ensure the score doesn't drop just because no one has voted yet.

---

## 🔌 Integration Guide for Teammates

### For the Dashboard Teammate:
- **Queue Logic:** Filter reports by `verification_status`.
  - `status == 'REVIEW_NEEDED'`: The "Needs Investigation" tab.
  - `status == 'REJECTED'`: The "Spam/Trash" tab.
- **Recalculation:** The dashboard should call `POST /score/{report_id}/recalculate` when an officer manually changes a score or a vote period ends.

### For the Blockchain Teammate:
- **Hook Point:** In `mobile_auth.py`, right after `FinalScoreCalculator` returns `AUTO_VERIFIED`.
- **Logic:** You should create a background task (`BackgroundTasks` in FastAPI) to push the report to the chain so it doesn't slow down the mobile user's response.
- **Data:** Use the `combined_score` as the "Proof of Integrity" for the record.

### For the Notification Teammate:
- **Trigger:** We have an `ImpactScoreManager` utility. Every time a user's `impact_score` changes or a report status updates, you should trigger a push notification via the `fcm_token` stored in `UserProfile`.
