# StreetLight Notifications (Phase 1: DB-backed, Phase 2: FCM push)

This document explains the complete technical flow of notifications in StreetLight, including:

1. How notifications are stored (database model + migration)
2. Backend APIs used by the Flutter app
3. Exactly where notifications are triggered in the backend report/verification lifecycle
4. How push notifications work end-to-end (FCM token upload, server-side sending, tap routing/deep links)
5. How the Flutter UI consumes notifications (unread badge, notifications list, mark read, navigation)
6. How to test and troubleshoot the system
7. Known limitations/gaps and what’s next

---

## 1) System Overview

StreetLight notifications exist in two layers:

Layer 1 (Phase 1, reliable): DB-backed “in-app notifications”

- Created server-side as rows in `notifications`
- Flutter reads them using authenticated REST endpoints
- Used to show in-app bell badge, a notifications list, and mark-as-read state

Layer 2 (Phase 2, real-time): FCM push notifications (best-effort)

- Flutter uploads the device’s FCM token to the backend
- Backend sends an FCM message to the stored `user_profiles.fcm_token`
- Tap handling uses `data.route` to navigate to the appropriate screen
- Push delivery failure does not break in-app notifications because Phase 1 remains the source of truth

---

## 2) Data Model (Database)

### 2.1 Notifications table

SQLAlchemy model:

- `backend/model/notification.py`

Schema fields (created by migration):

- `id` (SERIAL PK)
- `user_id` (FK → `users.id`, indexed)
- `type` (string, indexed)
- `title` (string)
- `body` (text, nullable)
- `entity_type` (string, nullable)
- `entity_id` (int, nullable)
- `data` (JSONB, nullable)
- `dedupe_key` (string, nullable, unique when present)
- `created_at` (timestamp with timezone, default now)
- `read_at` (nullable timestamp)

Deduplication:

- `dedupe_key` is declared unique by the migration.
- Backend notification creation uses `dedupe_key` so repeated triggers (or recalculations) do not spam users.

Migration script:

- `backend/script/migrate_notifications.py`
- Runs automatically on startup via `backend/main.py`

Startup wiring:

- `backend/main.py` calls `migrate_notifications()` in the `startup_event()`.

---

## 3) Backend APIs (Authenticated)

Base prefix:

- `/notifications`

### 3.1 List notifications

- `GET /notifications`

Query parameters:

- `unread_only` (boolean, default `false`)
- `limit` (int, default `50`, min `1`, max `200`)
- `cursor` (int, optional pagination: returns `id < cursor`)

Auth:

- Requires current user via `get_current_user`

Response:

- `success: true/false`
- `count`
- `next_cursor` (or null)
- `notifications` array, each item contains:
  - `id`, `type`, `title`, `body`
  - `entity_type`, `entity_id`
  - `data`
  - `created_at`, `read_at`

Implementation file:

- `backend/routers/flutter/notifications.py`

### 3.2 Unread count

- `GET /notifications/unread-count`

Response:

- `success: true`
- `unread_count` (int)

Used by:

- Flutter Home bell badge

### 3.3 Mark read / mark unread

- `POST /notifications/{notification_id}/read`

Body:

- `{ "read": true }`

Behavior:

- If `read=true`, sets `read_at` to `now` (if null)
- If `read=false`, sets `read_at` back to `NULL` (mark unread)

Response:

- `success: true`
- `notification` (serialized)

---

## 4) Backend Trigger Points (Where Notifications Are Created)

Notifications are created server-side inside the existing report pipeline.

### 4.1 Community verification request created → notify nearby users

Trigger point:

- `backend/ai_layers/layer3_community_verification/community_engine.py`
- In `CommunityVerificationEngine.create_verification_request(...)`

When it runs:

- Called after a report is persisted and Layer 3 builds a `verification_requests` row.

How recipients are selected:

- Uses `UserProfile.last_known_lat` and `UserProfile.last_known_lng`
- `_find_nearby_users(...)` returns users within a radius (defaults to 500m)
- Reporter/author is excluded

Notification created (Phase 1):

- For each nearby user:
  - `type: "VERIFY_REQUEST"`
  - `title: "Verification needed nearby"`
  - `body: "A {category} was reported about {dist}m from you. Can you verify it?"`
  - `entity_type: "verification_request"`
  - `entity_id: request.id`
  - `data: { request_id, report_id, distance_m }`
  - `dedupe_key: "VERIFY_REQUEST:{uid}:{request.id}"`

Push sent (Phase 2, best-effort):

- After DB notification creation, backend attempts FCM send:
  - route/deep link: `/verification`
  - data: `{ route, request_id, report_id }`

Note:

- Push sending is “best-effort”. If FCM is not configured or fails, Phase 1 still exists in DB.

---

### 4.2 Report final score decision → notify reporter

Trigger point:

- `backend/routers/flutter/mobile_auth.py`
- In `create_report(...)` after `FinalScoreCalculator(db).calculate_final_score(report.id)`

When it runs:

- After Layer 5 scoring updates the report’s `verification_status` and may update `report.status` to `VERIFIED` or `REVIEW_NEEDED` or leave it as per logic for rejected.

Notification created (Phase 1):

- One notification for the reporter (deduped per status):
  - `type: "REPORT_STATUS"`
  - `entity_type: "report"`
  - `entity_id: report.id`
  - `data: { report_id, verification_status, combined_score }`
  - `dedupe_key: "REPORT_STATUS:{user_id}:{report.id}:{vstatus}"`

Message content:

- `VERIFIED`:
  - title: “Report verified”
  - body: “Your report has been auto-verified and sent for action.”
- `REVIEW_NEEDED`:
  - title: “Report under review”
  - body: “Your report needs officer review. You’ll be updated once a decision is made.”
- `REJECTED`:
  - title: “Report rejected”
  - body: “Your report was rejected due to low confidence. You can try submitting a clearer photo.”
- fallback (pending/unexpected):
  - title: “Report received”
  - body: “Your report was received and is being processed.”

Push sent (Phase 2, best-effort):

- route/deep link: `/notifications`
- data: `{ route: "/notifications", report_id, verification_status }`

---

## 5) FCM Push Notifications (Phase 2)

FCM works only if backend has Firebase Admin credentials and Flutter uploads a valid device token.

### 5.1 Flutter: FCM token upload

Files:

- `frontend/lib/services/push_notifications.dart`
- `frontend/lib/services/api_service.dart` (method)
- backend endpoint: `POST /users/fcm-token` in `backend/routers/flutter/users.py`

Process:

1. App starts → `PushNotifications.init(...)` runs
2. It requests notification permission (Android permission dialogs apply on modern Android)
3. It calls `FirebaseMessaging.instance.getToken()`
4. If a token exists:
  - Calls `ApiService.updateFcmToken(token)`
  - Backend stores it in `user_profiles.fcm_token`
5. On token refresh:
  - `onTokenRefresh.listen(...)` uploads the new token again

Deep link/tap routing:

- `FirebaseMessaging.onMessageOpenedApp.listen(...)`
- `FirebaseMessaging.instance.getInitialMessage()` (cold start)
- Both read `message.data["route"]`
- Supported routes by this project:
  - `/verification`
  - `/notifications`

Navigation uses:

- `navigatorKey` defined in `frontend/lib/main.dart`

### 5.2 Backend: FCM sending utility

File:

- `backend/utils/push.py`

How backend initializes Firebase Admin:

- `init_firebase()` uses `GOOGLE_APPLICATION_CREDENTIALS`
- It requires a service-account JSON file
- Best-effort: if it fails, it logs warnings and returns `False`

How messages are sent:

- `send_push_to_user(db, user_id, title, body, data)`
- Fetches `UserProfile.fcm_token`
- Sends `messaging.Message(notification=..., data=..., token=...)`
- Returns `True` if sent, `False` otherwise

Service-account env var:

- Must exist in runtime environment (not just committed code)

---

## 6) Flutter UI Consumption (Phase 1 + Deep links)

### 6.1 Home bell badge

File:

- `frontend/lib/screens/home_screen.dart`

Behavior:

- On Home load, Flutter calls:
  - `ApiService.getUnreadNotificationCount()`
- Displays `_unreadNotificationCount` as a badge

On bell tap:

- Opens `NotificationsScreen` at route `/notifications`

### 6.2 Notifications list screen

File:

- `frontend/lib/screens/notifications_screen.dart`

Behavior:

- Calls `ApiService.getNotifications(limit: 100)`
- Renders a list of notifications from the backend
- Shows unread/read state using `read_at`
- Allows user to:
  - tap an item → marks as read (if currently unread)
  - uses minimal deep link rules:
    - `type == "VERIFY_REQUEST"` → navigates to `/verification`
    - `type == "REPORT_STATUS"` → remains on notifications list (Phase 1 UX)

### 6.3 Push tap navigation

FCM tap payload includes `data.route`:

- For nearby verification push: route `/verification`
- For reporter status push: route `/notifications`

Flutter receives it in `PushNotifications.init(...)` and navigates accordingly.

---

## 7) End-to-End Flow Scenarios (Step-by-step)

### Scenario A: Reporter submits a report → reporter gets notification

1. User submits report from Flutter → backend `POST /reports/create`
2. Backend runs Layer 0/1/2/Cloudinary persist
3. Backend creates community verification request (Layer 3)
4. Backend runs Layer 5 final score calculation
5. Backend creates:
  - DB notification `REPORT_STATUS` for the reporter
6. Backend attempts FCM push to reporter device token
7. Flutter Home bell badge updates when:
  - app opens and fetches unread count
8. User taps push (if they got it) → Flutter navigates to `/notifications`
9. User sees notification in `NotificationsScreen`, taps it:
  - it becomes read (POST `/notifications/{id}/read`)

### Scenario B: Nearby user gets a “verify” request push

1. Report is created and Layer 3 creates `verification_requests`
2. Backend finds nearby users based on their `UserProfile.last_known_lat/lng`
3. For each nearby user:
  - creates DB notification `VERIFY_REQUEST`
  - attempts FCM push with `route=/verification`
4. User taps push:
  - Flutter navigates to `/verification`
5. User can vote using existing community verification endpoints

---

## 8) How to Test (Practical checklist)

### Pre-requisites

1. Ensure backend is running and DB contains correct schema (startup migration runs)
2. Ensure each test user is logged in on the app at least once
3. Ensure FCM token upload succeeded (backend logs)
4. Ensure `GOOGLE_APPLICATION_CREDENTIALS` is valid on the backend runtime

### Test checklist (Phase 1: DB notifications)

1. Login on Device A
2. Submit a report from Device A
3. Open `/notifications` on Device A
4. Verify you see a `REPORT_STATUS` notification
5. Tap the notification → it becomes read
6. Verify bell badge unread count decreases

Expected backend logs:

- notification creation in `mobile_auth.py`
- no reliance on FCM being configured

### Test checklist (Phase 2: FCM push)

1. Setup two devices/accounts: Device A (reporter) and Device B (nearby)
2. On each device:
  - open the app while logged in at least once
  - confirm backend received token:
    - look for `🔔 FCM token updated for user ID=...` from `backend/routers/flutter/users.py`
3. Put Device A and/or B in background
4. Device A submits a report near Device B:
  - Device B should receive `VERIFY_REQUEST` push (route `/verification`)
5. Tap push:
  - app should navigate to `/verification`
6. Device A should also receive `REPORT_STATUS` push:
  - tapping should navigate to `/notifications`

### Logs to check when debugging push

1. Backend logs from:
  - `backend/utils/push.py` initialization warnings if Firebase Admin is not configured
  - “Push failed user=...” warnings if a token is missing/invalid
2. Flutter logs (debug console) to confirm:
  - `PushNotifications.init()` runs
  - token upload occurs (can be inferred if backend logs show token update)

---

## 9) Security / Secrets

Never commit service-account credentials.

You should configure:

- Backend environment:
  - `GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/firebase-service-account.json`

The repository ignores service-account JSON files via:

- root `.gitignore` patterns:
  - `*service-account*.json`
  - `firebase-service-account*.json`

---

## 10) Known Limitations / Gaps (Current Implementation)

FCM push currently triggers only on two event types:

1. Nearby verification request created → `VERIFY_REQUEST`
2. Reporter final score decision after report submission → `REPORT_STATUS`

Currently NOT pushing (yet):

1. Officer manual approval events (if they happen via separate endpoint)
2. Blockchain “resolved” events from `/blockchain` router

UI limitations:

1. Foreground push display:
  - The app handles tap routing (`onMessageOpenedApp`, `getInitialMessage`)
  - It does not yet implement a full foreground handler (`FirebaseMessaging.onMessage`) that would show an in-app banner while app is open.

Token cleanup:

1. Backend logs push failures but does not automatically clear invalid tokens.

---

## 11) What to do next (Recommended improvements)

1. Add Android 13+ permission explicitly:
  - `android.permission.POST_NOTIFICATIONS`
2. Implement `FirebaseMessaging.onMessage` to show an in-app banner/snackbar while app is foregrounded
3. Push on additional lifecycle events:
  - officer approval
  - resolved/blockchain confirmation
4. Clear invalid FCM tokens after detecting token-not-registered type errors

