# StreetLight — AI-Powered Civic Complaint Management

> Final Year Project · PUCIT · 2025  
> AI-driven platform for reporting and resolving municipal infrastructure issues in Pakistan.

---

## What It Does

Citizens photograph and submit complaints (potholes, garbage, broken streetlights) via a **Flutter mobile app**. An AI pipeline validates each report, GPS-routes it to the correct city department, notifies the responsible officer by email, and tracks the issue through a Kanban workflow until resolution. Municipal officials manage everything through a **React web admin portal**.

---

## Repository Structure

```
streetlight/
├── backend/               # FastAPI REST API + AI pipeline
├── municipal-admin/       # React admin portal (this doc focuses here)
├── frontend/              # Flutter mobile app (citizen-facing)
├── blockchain-layer/      # Ethereum smart contracts (Solidity)
├── streetlight_layers/    # AI validation engine modules
└── documentations/        # Additional project docs
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile App | Flutter 3 |
| Backend API | FastAPI (Python 3.11) + SQLAlchemy |
| Admin Portal | React 18.2 + Vite 5 + Tailwind CSS 3.4 |
| Database | PostgreSQL |
| Auth | JWT (HS256, 30-day expiry) |
| File Storage | Cloudinary |
| Blockchain | Ethereum / Solidity |
| Email | Gmail SMTP via App Password |
| Push Notifications | Firebase FCM |
| Maps | Leaflet / react-leaflet |
| Kanban DnD | @hello-pangea/dnd v18 |

---

## Admin Portal — Role System

Three roles with automatic data scoping enforced at the **backend query level** (not just UI):

| Role | Scope | Capabilities |
|---|---|---|
| `super_admin` | All Pakistan | All pages, all users, audit log, full analytics |
| `city_admin` | Own city only | Create dept officers, city analytics, departments |
| `dept_officer` | Own dept only | Update complaint stages, add notes, view own audit trail |

### Login Convention
Admin login emails use `@streetlight.local` (system identifiers, not real inboxes).  
Each user has a separate `notification_email` for real email alerts (set via My Profile).

---

## Admin Portal — Pages

| Page | Route | Roles | Description |
|---|---|---|---|
| Sign In | `/signin` | Public | Split-panel dark luxury login |
| Dashboard | `/dashboard` | All | KPI cards, trends, city breakdown (super_admin) |
| Complaint Management | `/complaint-management` | All | Filtered/searchable table + CSV export |
| Complaint Detail | `/complaint-detail/:id` | All | Full report, AI scores, internal notes, audit log |
| Resolution Board | `/resolution-board` | All | Drag-and-drop Kanban (6 stages) |
| Hotspot Map | `/hotspot-map` | All | Leaflet map with severity-colored complaint markers |
| Analytics | `/analytics` | All | Charts, trends, dept performance, CSV export |
| Transparency | `/transparency` | SA, CA | Public accountability view — resolution rates |
| Departments | `/departments` | SA, CA | Live routing table from API |
| User Roles | `/user-roles` | SA, CA | Create/edit admin users (role-aware) |
| Audit Log | `/audit-log` | All | Immutable trail of every stage change and note |
| My Profile | `/my-profile` | All | Update notification email |

---

## Backend API — Admin Endpoints

All require `Authorization: Bearer <token>`. Data is **automatically scoped** by role.

```
POST   /admin/auth/login               # Authenticate, get JWT
GET    /admin/reports                  # List complaints (filters: stage, search, date_from, city)
GET    /admin/reports/kanban           # Kanban board grouped by stage
GET    /admin/reports/:id              # Full report with logs
PATCH  /admin/reports/:id/stage        # Move to new stage (triggers email+FCM on RESOLVED)
POST   /admin/reports/:id/note         # Add internal note
GET    /admin/dashboard/overview       # KPI counts + city_breakdown (super_admin)
GET    /admin/dashboard/analytics      # Time-series analytics (?days=7|30|90|365)
GET    /admin/users                    # List admin users
POST   /admin/users                    # Create user (city_admin limited to dept_officer)
PATCH  /admin/users/:id                # Update user (self can update notification_email only)
GET    /admin/routing                  # Routing table (city→dept→officer mapping)
GET    /admin/audit-logs               # Paginated audit trail (?report_id=, skip, limit)
```

---

## Complaint Lifecycle

```
Citizen submits (Flutter)
  → AI validates (5 layers: image, GPS, NLP, trust score, duplicate)
  → GPS → city + dept routing
  → Officer notified via email (notification_email)
  → Officer updates stage via Kanban / detail page
  → On RESOLVED: citizen notified by email + FCM push
  → All stage changes written to append-only audit log
```

### Kanban Stages

`NEW` → `PENDING_VERIFICATION` → `VERIFIED` → `IN_PROGRESS` → `AWAITING_FEEDBACK` → `RESOLVED`

---

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:
```env
DATABASE_URL=postgresql://user:pass@localhost/streetlight
SECRET_KEY=your_jwt_secret_32chars_minimum
SMTP_USER=your.gmail@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password (16 chars)
SMTP_FROM_NAME=StreetLight
ADMIN_BASE_URL=http://localhost:5173
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

```bash
python script/seed_routing_table.py   # Seed users + routing
uvicorn main:app --reload --port 8000
```

### Admin Portal

```bash
cd municipal-admin
npm install
```

Create `municipal-admin/.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

```bash
npm run dev     # → http://localhost:5173
npm run build   # Production build
```

---

## Default Credentials (seed data)

| Role | Email | City | Dept |
|---|---|---|---|
| super_admin | `superadmin@streetlight.local` | — | — |
| city_admin | `lahore.admin@streetlight.local` | Lahore | — |
| city_admin | `faisalabad.admin@streetlight.local` | Faisalabad | — |
| dept_officer | `ahmad.raza@streetlight.local` | Lahore | LMC |
| dept_officer | `sara.khan@streetlight.local` | Lahore | LWMC |
| dept_officer | `bilal.chaudhry@streetlight.local` | Faisalabad | FMC |
| dept_officer | `ayesha.nawaz@streetlight.local` | Faisalabad | FWMC |

---

## Key Implementation Notes

- **StrictMode removed** from `main.jsx` — required for `@hello-pangea/dnd` compatibility with React 18
- **Role scoping** is enforced in `_base_query()` on the backend — frontend role checks are secondary
- **Notification emails** are separate from login emails — officers set them via My Profile
- **Optimistic UI** on Kanban drag — reverts to server state on API failure
- **CSV export** in Complaint Management fetches up to 1000 filtered records
- **City breakdown** in SuperAdmin Dashboard shows live `resolved / total` per city
- **Audit log** is append-only (`ReportLog` model) — never updated or deleted

---

## Email Setup (Gmail App Password)

1. Enable 2-Step Verification on your Google account
2. Go to **Security → App Passwords**
3. Generate a password for "Mail"
4. Paste the 16-character password as `SMTP_PASSWORD` in `.env`
5. Free tier: ~500 emails/day

---

## Cities & Departments (MVP)

```
Lahore
  ├── LMC  (Lahore Metropolitan Corporation)     → roads, potholes, infrastructure
  └── LWMC (Lahore Waste Management Company)     → garbage, trash, waste

Faisalabad
  ├── FMC  (Faisalabad Metropolitan Corporation) → roads, potholes, infrastructure
  └── FWMC (Faisalabad Waste Management Company) → garbage, trash, waste
```

---

## Database Models

| Model | Table | Purpose |
|---|---|---|
| `User` | `users` | Admin users with role, city, dept, notification_email |
| `UserProfile` | `user_profiles` | Citizen profiles with FCM token, trust score |
| `Report` | `reports` | Complaints with AI scores, GPS, stage, category |
| `ReportLog` | `report_logs` | Append-only audit trail for every action |
| `RoutingTable` | `routing_table` | city + dept → officer mapping |

---

*StreetLight — Illuminating city operations.*
