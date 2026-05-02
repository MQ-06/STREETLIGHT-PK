# StreetLight Admin Panel — Testing Guide

This document describes how to manually verify the municipal-admin SPA against the FastAPI backend. Adjust base URLs and credentials for your environment.

## Prerequisites

1. **Backend** running with DB migrated and seeded (`StreetLight` API root responds at `/health`).
2. **Frontend** dev server (`npm run dev`) or production build served with correct API base URL (see `VITE_*` / proxy config).
3. **Test accounts** — one user per role at minimum:
   - `super_admin` — national scope, Organization + Transparency visible.
   - `city_admin` — `city` set on user; city-scoped lists and dashboards.
   - `dept_officer` — active row in `routing_table` linking `officer_id` → `city` + `department`; dept-scoped data.

Optional: Firebase configured for push (not required for most admin UI tests).

---

## Role × navigation smoke test

| Route | super_admin | city_admin | dept_officer |
|-------|-------------|------------|--------------|
| `/dashboard` | National overview | City overview | Dept overview |
| `/complaint-management` | All scoped reports | City-scoped | Dept-scoped |
| `/resolution-board` | Scoped Kanban | Scoped | Scoped |
| `/hotspot-map` | Scoped pins | Scoped | Scoped |
| `/analytics` | Dark SA dashboard (`SuperAdminAnalytics`) | Modular analytics + scope tabs | Same as city_admin pattern |
| `/organization` | Yes | Yes | Hidden |
| `/transparency` | Yes | Yes | Hidden |
| `/audit-log` | Yes | Yes | Yes |
| `/my-profile` | Yes | Yes | Yes |

**Checks**

- Sign out clears token and redirects to `/signin`.
- Wrong role cannot open Organization (redirect to `/dashboard`).

---

## Authentication

1. Open `/signin`, log in with valid admin credentials.
2. Confirm JWT stored (application storage per your `auth.js` implementation).
3. Reload `/dashboard` — still authenticated.

**Failure modes**: CORS misconfiguration, wrong API base URL, 401 on all `/admin/*` calls.

---

## Dashboard (`/dashboard`)

Per role, verify:

1. **Overview** loads without errors (`GET /admin/dashboard/overview`).
2. **Mini trend** reflects last 7 days (`GET /admin/dashboard/analytics?days=7` — `trend` array).
3. **Kanban counts** match intuition after creating/moving test complaints (optional cross-check vs DB).
4. **Recent complaints** table loads (`GET /admin/reports?skip=0&limit=6` or configured limit).

**Dept officer**: remove or deactivate routing row — expect empty or reduced counts per backend rules.

---

## Complaints list (`/complaint-management`)

1. Table loads (`GET /admin/reports?skip=&limit=` — respect backend `limit` max).
2. Filters: stage, date_from, search query (also global search from top bar where wired).
3. Export CSV if present — matches API contract for that page.
4. Row navigates to `/complaint-detail/:id`.

---

## Complaint detail (`/complaint-detail/:id`)

1. Loads single report (`GET /admin/reports/{id}` or equivalent in codebase).
2. Stage badge matches API `kanban_stage`.
3. After-image upload (if applicable) succeeds and moves workflow toward `AWAITING_FEEDBACK` per backend.

---

## Resolution Board (`/resolution-board`)

1. Columns load (`GET /admin/reports/kanban`).
2. Drag card to another column → `PATCH /admin/reports/{id}/stage` with `{ "stage": "<COLUMN>" }`.
3. On failure, UI rolls back / reloads (watch network tab).
4. **Refresh** reflects changes made outside this tab (another user, mobile app, or agent). There is **no live WebSocket** — stale boards are expected until refresh.

---

## Hotspot map (`/hotspot-map`)

1. Pins/clusters load from scoped reports endpoint used by map hook.
2. Filter sidebar affects visible pins.
3. Detail panel opens and matches selected report.

---

## Analytics (`/analytics`)

### Super admin

1. KPI / charts / alerts load from `/admin/analytics/*` modules.
2. Change **days** (7 / 30 / 90) — all widgets refetch with same `days` parameter family.
3. PDF export / report modal — hits analytics PDF endpoint and downloads/opens PDF.

### City admin / dept officer

1. Default scope matches JWT claims (`city`, `department`).
2. Scope tab strip changes `scope` / `scope_id` query params — data updates.
3. Alerts feed (`GET /admin/analytics/alerts`) returns list; messages should track scoped DB aggregates (rule-based, not arbitrary constants).

---

## Organization (`/organization`)

**Departments tab**

- Super admin: routing rows CRUD via `/admin/routing/*` (per implementation).
- City admin: city-limited routing.

**Users tab**

- Create/update officers; assign roles; verify listings scope.

---

## Transparency (`/transparency`)

1. KPIs load from **`/admin/dashboard/overview`** plus **`/admin/dashboard/analytics`** (`days=30` and `days=365`).
2. Chart KPIs use the **same rolling windows as analytics** (not “all time” unless you choose a large `days`).
3. **Cities covered** and city cards come from **`overview.city_breakdown`** (super admin) or **viewer city + overview totals** (city admin).

---

## How agents relate to what you see in admin

- **Complaint agent** runs every **15 minutes** (when the API starts). It reads reports from the database and may change **status / Kanban** (for example auto-verify or send items to pending verification). It does **not** push updates to your browser.
- **Resolution agent** runs when certain **API actions** happen (for example **after-image upload** or dragging a card to **RESOLVED**). It may send **FCM** to the citizen and later **finalize** closure.
- **Resolution Board** **refetches every 60 seconds** (when the tab is visible) so column changes from agents or the mobile app appear without pressing Refresh.
- **`GET /test-agent`** runs **one** complaint-agent cycle — call it while logged in as **super_admin** (requires a normal auth token).

---

## Audit log (`/audit-log`)

1. Entries load (`GET /admin/audit/*` per router).
2. `ai_managed` rows display as AI/agent attribution where implemented.

---

## Profile (`/my-profile`)

1. Loads current user; optional PATCH/update flows succeed.

---

## Backend-agent behaviour (manual integration)

Complaint agent cycle runs on an **interval scheduler** when the API process starts (`startup` in `main.py`). Cycle duration: **15 minutes** (see `agent_scheduler.py`).

To force one cycle immediately (authenticated):

```http
GET /test-agent
Authorization: Bearer <super_admin JWT>
```

Only **`super_admin`** may call this endpoint.

**What to observe**

1. Pending reports with high scores may move toward verified Kanban stages without manual drag (depends on `agent_rules` / `execute_action`).
2. `AWAITING_FEEDBACK` reports older than configured auto-close window may finalize via `check_auto_close` (see `AUTO_CLOSE_DAYS` in agent config).

---

## Resolution / closure chain (high level)

Use this checklist when testing **closed** complaints:

1. Officer workflow reaches **after-image** / **resolved** stages per product rules.
2. Citizen confirms via mobile API → `finalize_resolution` path OR timeout triggers auto-close.
3. **CLOSED** may depend on **blockchain** write success — if chain fails, report can remain **RESOLVED** until retry (check `ReportLog` notes).

---

## Regression checklist (quick)

- [ ] All roles log in and land on correct dashboard variant.
- [ ] Scoped endpoints never leak other cities/departments for city_admin/dept_officer.
- [ ] Kanban PATCH validates unknown stages with 400.
- [ ] Large list `limit` stays within backend `Query(..., le=...)`.
- [ ] CSV/export endpoints match analytics scope expectations.

---

## Suggested test data

- At least **3 reports** per category (`POTHOLE`, `TRASH`) spanning multiple Kanban stages.
- One report per terminal stage (`RESOLVED`, `CLOSED`) for analytics verification.
- Optional: duplicate routing officers to test uniqueness constraints.
