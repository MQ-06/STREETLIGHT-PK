## STREETLIGHT Project Status & App Enhancements

### 1. High-Level Overview

The STREETLIGHT project consists of:

- **Backend**: FastAPI-based civic reporting and AI pipeline (image validation, classification, GPS verification, fraud detection, community verification, trust, and final scoring).
- **Frontend App**: Flutter-based citizen app for reporting issues, viewing a feed, community verification, and tracking impact.
- **Admin / Municipal**: Separate municipal/admin module (not covered in this document, per current scope).
- **Documentation**: AI engine implementation docs plus capstone deliverables describing the layered architecture and scoring logic.

Overall, the **core functionality is largely complete**: citizens can sign up, log in, submit AI-validated reports, support/verify others’ reports, participate in community verification, and see their profile and impact. What mostly remains is **product polish, UX consistency, and some production-grade integrations** (logout, auth-aware startup, real Explore data, notifications).

---

### 2. Backend Status

#### 2.1 Architecture & Stack

- **Framework**: FastAPI application (entry point in `main.py`).
- **Database & ORM**: PostgreSQL via SQLAlchemy.
- **Auth & Security**:
  - Argon2-based password hashing.
  - JWT-based authentication using `python-jose`.
  - Role-based access control for admin endpoints.
- **AI & Computer Vision**:
  - PyTorch and TorchVision models.
  - OpenCV and related utilities for image validation and severity estimation.
- **External Services**:
  - Cloudinary for image storage.
  - HTTP APIs and geocoding for GPS verification.
- **CORS & Middleware**:
  - CORS middleware configured for the Flutter app.
  - Startup hooks to initialize services and clean temp files.

#### 2.2 Implemented Backend Features

- **User & Auth**
  - Citizen signup with CNIC/email uniqueness, secure password hashing.
  - Login returning JWT with user ID, email, and role.
  - Password reset:
    - Endpoint to request a reset token.
    - Endpoint to reset password using the token.
  - Role-based guards for admin/municipal routes.

- **Report Lifecycle & AI Pipeline**
  - Report creation endpoint used by the app that:
    - Validates required data (image, GPS).
    - Runs multi-layer AI pipeline:
      - Image validation (quality, brightness, framing).
      - Classification (e.g., potholes/garbage) and severity heuristics.
      - GPS landmark verification and distance checks.
    - Performs fraud checks:
      - GPS spoofing detection.
      - Spam and rate-limiting (hourly reports).
      - Duplicate-of-id linking for similar reports.
    - Uploads images to Cloudinary.
    - Persists a rich `Report` record with:
      - Status (pending/verified/in-progress/resolved, etc.).
      - AI scores and metadata.
      - Fraud flags and auxiliary fields for analysis.

- **Community Verification & Scoring**
  - Community verification requests for eligible reports.
  - Vote handling (YES/NO) and tallying with impact/weighting.
  - Trust/history layer that computes per-user trust scores using:
    - Account age.
    - Past reports and resolution history.
    - Fraud flags and community behavior.
  - Final score calculation layer that combines:
    - AI confidence and severity.
    - Community verification results.
    - User trust score.
  - Verification status classification (e.g., auto-verified, review-needed, rejected).

- **Engagement & Profile APIs**
  - Report feed with pagination, join to user profile and interactions, and comment counts.
  - Interactions:
    - Support (toggle).
    - Verify (toggle and promotion to verified above a threshold).
  - Comments:
    - Fetch comments for a report.
    - Add comment.
    - Delete own comment.
  - User profile:
    - Impact score and counters.
    - FCM token storage for future notifications.
    - My-reports endpoint with status breakdown.
  - Trust and score endpoints:
    - Per-user trust scores.
    - Per-report final score recalculation endpoints.

#### 2.3 Backend Gaps & Future Work

- **Logout / Token Management**
  - No dedicated `/logout` endpoint or token blacklist.
  - Stateless JWT is currently cleared only on the client side.

- **Push Notifications**
  - Backend stores FCM tokens and includes TODOs to notify nearby users.
  - Actual notification sending (e.g., Firebase HTTP API integration) is not implemented.

- **Duplicate Detection (Image Hash)**
  - Image-hash-based duplicate detection is present but commented out in the AI engine.
  - Duplicate-of-id logic is implemented in fraud detection, but early image-hash screening could be re-enabled.

- **Status Semantics**
  - `ReportStatus` includes states like `PENDING`, `VERIFIED`, `IN_PROGRESS`, `RESOLVED`, `TODO`.
  - Frontend sometimes expects or renders slightly different labels (e.g., “REPORTED”).
  - A consistent mapping between backend enums and frontend labels is needed.

- **Production-Grade Password Reset**
  - Reset tokens are currently returned in responses (development shortcut).
  - A production setup should send tokens via email, not expose them directly to the app.

---

### 3. Frontend App Status (Flutter)

#### 3.1 Architecture & Stack

- **Framework**: Flutter (Material).
- **Routing**: Named routes for all major screens:
  - Splash, Landing, Login, Register.
  - Home, Explore, Profile, Report Issue.
  - Forgot Password, Reset Password.
  - Verification.
- **State Management**:
  - Primarily `StatefulWidget` + `setState`.
  - Persistent data via `SharedPreferences`:
    - Auth token (through `ApiService`).
    - Basic user session data (name, email, some stats) via `UserSession`.
- **API Layer**:
  - `ApiService` centralizes HTTP calls and base URL selection (web, emulator, mobile IP).
  - Handles:
    - Auth (signup, login, forgot/reset password, logout).
    - Reports (feed, create, my-reports, support/verify).
    - Comments (get/add/delete).
    - User profile (impact and stats).
    - Community verification (pending, vote, status).

#### 3.2 Implemented App Features

- **Onboarding & Authentication**
  - Splash screen with animation transitions to Landing.
  - Landing screen with clear CTAs to Login and Register.
  - Login screen:
    - Validates input, calls backend, stores token and user info.
    - Navigates to Home on success.
  - Registration screen:
    - Collects required details (including CNIC).
    - Uses backend signup endpoint and navigates to login on success.
  - Forgot/Reset Password:
    - Forgotten password screen calls backend to generate a reset token.
    - Reset password screen uses token (provided via navigation args) and sets new password.

- **Home / Feed**
  - Infinite-scroll feed of real reports from backend, including:
    - Images, description, location, and status badges.
    - Support and verify buttons with optimistic UI + server sync.
    - Comment button that opens a bottom sheet:
      - Loads comments.
      - Allows posting and deleting comments.
  - Notification bell showing pending community verification requests (count and list).
  - 401 handling:
    - If feed request fails with unauthorized, the app clears token and returns the user to login (automatic logout on expiry).

- **Report Issue Flow**
  - Image selection from camera or gallery with appropriate permissions.
  - Location gathering:
    - GPS and reverse geocoding.
    - Static OSM map preview centered on the chosen coordinates.
  - Submission:
    - Sends multipart request to backend with image and GPS data.
    - Handles AI errors gracefully and maps them to user-friendly messages (blurry, dark, wrong category, GPS issues).

- **Profile & Impact**
  - Profile screen combining:
    - Locally stored name and avatar.
    - Backend impact score and stats.
  - Badge/tier system based on impact score with detailed explanation bottom sheet.
  - Tabs:
    - My reports.
    - Resolved reports.
    - Impact summary.
  - Report cards using real backend data with status and resolution/impact visualization.

- **Community Verification**
  - Dedicated screen listing pending verification requests near the user.
  - Per-request card with image, distance, age, and vote counts.
  - YES/NO voting that calls backend and removes the card on success.

- **Explore (Prototype)**
  - Map-based view with markers and a rich bottom sheet.
  - Shows sample complaints and stats using hardcoded demo data.
  - Demonstrates the intended UX for regional/insights view.

#### 3.3 App Gaps & Known Issues

- **Logout Functionality**
  - No explicit logout button on any major screen.
  - `ApiService.logout()` exists but is only used for 401 failures in the feed.
  - Users cannot proactively log out from the app.

- **Auth-Aware Startup**
  - Splash and Landing screens do not check for an existing valid token.
  - Even if already logged in, users always see Landing before reaching Home.

- **Explore Screen Integration**
  - Explore currently uses hardcoded data and does not talk to the backend.
  - It does not show real reports, nor does it allow actions like support/verify.

- **Notifications**
  - Backend stores FCM tokens, but:
    - App does not integrate Firebase Messaging yet.
    - No in-app handling of push notifications.

- **Status & Model Alignment**
  - Some frontend UI text (e.g., “REPORTED”) doesn’t perfectly match backend status enums (e.g., `PENDING`).
  - Legacy `UserSession` methods for local-only auth (register/validate login) are still present but not actually used, which can confuse future development.

- **Search & Filters**
  - Home screen search bar is currently visual only:
    - No local filtering of list.
    - No backend query support wired yet.

- **Navigation Consistency**
  - Bottom navigation is implemented separately on multiple screens.
  - Different screens use a mix of `push`, `pushReplacement`, and `pushNamedAndRemoveUntil`, leading to slightly inconsistent backstack behavior.

---

### 4. Done vs Left – Summary

#### 4.1 What’s Done

- **Backend**
  - Stable FastAPI service with:
    - Secure signup/login/reset and JWT-based auth.
    - Rich AI-driven report creation and verification pipeline.
    - Community verification, trust, and final scoring.
    - User profile, impact, comments, and engagement endpoints.
- **Frontend App**
  - Full citizen-facing flow:
    - Onboarding, login, register, forgot/reset password.
    - Home feed with interactions and comments.
    - AI-powered report creation (camera, location, map).
    - Profile and impact tracking.
    - Community verification screen.
  - Visual/UX quality is high and close to production-ready.

#### 4.2 What’s Left / High-Priority Gaps

- **Logout UX**
  - Add visible logout action(s) and clear both token and local session data.
  - Optionally, plan for backend-side token invalidation in the future.

- **Auth-Aware Navigation**
  - Skip Landing for users with a valid token and route directly to Home.
  - Introduce a shared auth guard for all private routes.

- **Explore with Real Data**
  - Replace hardcoded sample data with real backend reports filtered by location or city.
  - Support map interactions and navigation to a detailed report view.

- **Notifications**
  - Integrate Firebase Messaging on the app side.
  - Implement backend push notification service using stored FCM tokens.

- **Consistency & Cleanup**
  - Align enum/status naming between backend and frontend.
  - Remove or clearly isolate legacy local-auth methods in `UserSession`.
  - Unify bottom navigation behavior across screens.

- **Production-Grade Reset & Monitoring**
  - Replace dev-style password reset token handling with email delivery.
  - Consider adding better logging/metrics around AI decisions, fraud flags, and verification for operations.

---

### 5. Recommended Next Steps (App-Focused)

- **Step 1: Implement Logout**
  - Add a logout button on the Profile screen (and optionally in a global menu).
  - Hook it to:
    - Clear auth token via `ApiService`.
    - Clear any user data in `UserSession`.
    - Navigate to Landing or Login with stack cleared.

- **Step 2: Auth-Aware Startup**
  - On app startup, check for a stored token.
  - If present and valid, route directly to Home; otherwise, go to Landing.
  - Consider a small “bootstrap” widget for this decision logic.

- **Step 3: Real Data for Explore**
  - Add backend support for location-based report feeds (if not already present).
  - Connect Explore to that endpoint and replace hardcoded complaints.

- **Step 4: Notifications**
  - Integrate Firebase Messaging in the Flutter app.
  - Implement backend notification sending for:
    - New nearby verification requests.
    - Report status changes.
    - Key impact milestones.

- **Step 5: Clean-Up and Alignment**
  - Standardize status labels across backend and app.
  - Remove dead/local-only auth code from `UserSession`.
  - Extract a shared bottom-nav widget and standardize navigation patterns.

