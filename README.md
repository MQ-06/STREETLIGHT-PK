
<div align="center">
  <img src="frontend/assets/images/logo.jpg" alt="StreetLight PK" width="180" />

# StreetLight PK

### AI-Powered Civic Complaint Intelligence for Pakistan

**Report it. Verify it. Fix it. Prove it.**

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Ethereum](https://img.shields.io/badge/Ethereum-Sepolia-3C3C3D?style=for-the-badge&logo=ethereum&logoColor=white)](https://ethereum.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com/)

<br/>

[![Download App](https://img.shields.io/badge/🚀%20Download%20the%20App-Visit%20Our%20Site-00C853?style=for-the-badge)](https://streetlight-page.vercel.app/)

> *PUCIT — BS Information Technology — Final Year Project 2026*

</div>

---

## The Problem

Pakistan's cities lose billions annually to unresolved civic failures. Citizens report broken roads and overflowing garbage — those reports vanish into a void. No accountability. No proof. Nothing fixed.

**StreetLight changes that.** A citizen photographs a problem. A 5-layer AI validates and scores it. The community verifies it. The right department gets it automatically. Everything goes on the blockchain. And the citizen confirms when it's actually fixed.

---

## 🎬 Demo

<div align="center">

*Click the thumbnail to watch the full demo*

[![StreetLight Demo](https://drive.google.com/thumbnail?id=1x070kizgMQulYHP8RQCBdd3EdAOL-qJS&sz=w1280)](https://drive.google.com/file/d/1x070kizgMQulYHP8RQCBdd3EdAOL-qJS/view?usp=sharing)

[![Watch Demo](https://img.shields.io/badge/▶%20Watch%20Full%20Demo-FF0000?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1x070kizgMQulYHP8RQCBdd3EdAOL-qJS/view?usp=sharing)
&nbsp;&nbsp;
[![Download App](https://img.shields.io/badge/🚀%20Get%20the%20App-00C853?style=for-the-badge)](https://streetlight-page.vercel.app/)

</div>

---

## What's Inside

<table>
<tr>
<td width="50%">

**📸 Instant Reporting**
Snap → Pin → Submit in 30 seconds

**🤖 5-Layer AI Pipeline**
Quality check → Classification → Fraud detection → Community votes → Trust score

**🗳️ Community Verification**
Nearby citizens vote, weighted by reputation

**🔗 Blockchain Proof**
Every verified complaint locked on Ethereum Sepolia

**🗺️ Smart Auto-Routing**
GPS assigns to LMC / LWMC / FMC / FWMC automatically

</td>
<td width="50%">

**📊 Municipal Kanban Portal**
Drag-drop 6-stage workflow for officers

**🔔 Real-time Alerts**
FCM push + email at every status change

**🧠 Agentic AI Background Jobs**
Auto-escalate stalled reports, auto-close resolved ones

**🔐 Role-Based Access**
Super admin → city admin → dept officer, scoped at the query level

**📋 Immutable Audit Trail**
Every action, append-only, forever

</td>
</tr>
</table>

---

## Architecture

```
 ┌─────────────────────────────────────────────────────────┐
 │               CITIZEN  ·  Flutter App                    │
 │          Photo  +  GPS  +  Description                   │
 └───────────────────────┬─────────────────────────────────┘
                         │  submit
                         ▼
 ┌─────────────────────────────────────────────────────────┐
 │            BACKEND  ·  FastAPI on Render                 │
 │                                                          │
 │  ╔═══════════════ 5-LAYER AI PIPELINE ════════════════╗ │
 │  ║                                                     ║ │
 │  ║  L0 Input ──► L1 EfficientNet ──► L2 Fraud Check  ║ │
 │  ║  Quality        Classify +          Duplicates      ║ │
 │  ║  GPS/Blur       Severity            GPS Spoof       ║ │
 │  ║                                     Spam Guard      ║ │
 │  ║                                                     ║ │
 │  ║  L3 Community ──► L4 Trust ──► L5 Final Score      ║ │
 │  ║  Weighted votes   Reputation    AI×0.4 + Com×0.3   ║ │
 │  ║  ±500m radius     Fraud flags   + Trust×0.3        ║ │
 │  ║                                                     ║ │
 │  ║  ≥85 → AUTO_VERIFY  │  60-84 → REVIEW  │ <60 → ✗  ║ │
 │  ╚═════════════════════════════════════════════════════╝ │
 │                                                          │
 │  [Agentic AI Scheduler]  [Smart Router]  [Web3 Writer]  │
 │  Auto-close / Escalate   GPS → Dept       Sepolia hash  │
 │                                                          │
 │  Supabase PostgreSQL  ·  Cloudinary CDN  ·  Firebase FCM│
 └──────────────┬──────────────────────┬───────────────────┘
                │                      │
                ▼                      ▼
 ┌──────────────────────┐  ┌──────────────────────────────┐
 │   INFERENCE SERVICE  │  │    ADMIN PORTAL  ·  Vercel   │
 │   HuggingFace Spaces │  │                              │
 │   EfficientNet-B3    │  │  Kanban · Heatmap · Analytics│
 │   FastAPI : 7860     │  │  Audit Log · RBAC · CSV      │
 └──────────────────────┘  └──────────────────────────────┘
```

---

## The 5-Layer AI Pipeline

```
SUBMIT ──► [L0] ──► [L1] ──► [L2] ──► SAVE TO DB ──► [L3] ──► [L4] ──► [L5] ──► DECISION
```

| Layer | Name | Does What | Output |
|:---:|---|---|:---:|
| **L0** | Input Validation | Blur, brightness, GPS, timestamp checks | Pass / ✗ |
| **L1** | AI Engine | EfficientNet-B3 classifies category + severity | Confidence 0–100 |
| **L2** | Fraud Detection | Impossible travel, duplicates (≤10m/14d), spam (>20/hr) | Pass / Block |
| **L3** | Community | Weighted votes from ±500m nearby users (min 3 votes, 48h) | Score 0–100 |
| **L4** | Trust History | User reputation: age + frequency + fraud flags | Score 0–100 |
| **L5** | Final Score | `AI×0.4 + Community×0.3 + Trust×0.3` → verdict | Auto/Review/Reject |

```
Score ≥ 85  ──►  AUTO_VERIFY   ──►  Blockchain + Route to Officer
Score 60–84 ──►  REVIEW_NEEDED ──►  Officer Investigates
Score  < 60 ──►  REJECTED      ──►  Citizen Notified
```

---

## Report Lifecycle

```
📱 Citizen Submits
       │
   [L0 – L2]  ──── ✗ Invalid / Fraud ──────────────► Rejected
       │
   💾 Saved
       │
   [L3 – L5]
       │
       ├── ✅ AUTO_VERIFY (≥85) ──► 🔗 Blockchain ──► 📧 Officer Notified
       │                                                       │
       │                                               🔄 IN_PROGRESS
       │                                                       │
       │                                          📷 After-image uploaded
       │                                                       │
       │                                        👍 Citizen Confirms Fix
       │                                                       │
       │                                               ✅ RESOLVED
       │
       ├── 🔍 REVIEW_NEEDED (60–84) ──► Officer Reviews Manually
       │
       └── ❌ REJECTED (<60) ──► Citizen Notified
```

---

## Tech Stack

<table>
<tr><th>Component</th><th>Stack</th></tr>
<tr>
<td><b>📱 Mobile App</b></td>
<td>Flutter 3 · Geolocator · flutter_map · FCM · Material Design</td>
</tr>
<tr>
<td><b>⚡ Backend API</b></td>
<td>FastAPI · SQLAlchemy 2.0 · PostgreSQL · Cloudinary · JWT · APScheduler</td>
</tr>
<tr>
<td><b>🧠 ML Inference</b></td>
<td>EfficientNet-B3 · PyTorch · timm · OpenCV · Docker · HuggingFace Spaces</td>
</tr>
<tr>
<td><b>🖥️ Admin Portal</b></td>
<td>React 18 · Vite · Tailwind CSS · Leaflet · Recharts · @hello-pangea/dnd</td>
</tr>
<tr>
<td><b>🔗 Blockchain</b></td>
<td>Solidity 0.8.19 · Hardhat · OpenZeppelin · Web3.py · Alchemy · Sepolia</td>
</tr>
<tr>
<td><b>☁️ Infrastructure</b></td>
<td>Render · Vercel · Supabase · HuggingFace Spaces · Firebase · Cloudinary</td>
</tr>
</table>

---


## Smart Contract

**Contract:** `StreetLight.sol` · **Network:** Ethereum Sepolia
**Address:** `0xa4bDa1C4EB8C4E04B01B03Bb0d8ec990F5ED128b`

> Privacy-first — only SHA-256 image hashes and Keccak location hashes go on-chain. No raw images, no coordinates, no PII.

Events emitted: `ComplaintVerified` · `ComplaintResolved`

---

## Getting Started

<details>
<summary><b>🐍 Backend</b></summary>

```bash
cd backend
pip install -r requirements.txt
# fill in your .env
python script/seed_routing_table.py
uvicorn main:app --reload --port 8000
```
</details>

<details>
<summary><b>⚛️ Admin Portal</b></summary>

```bash
cd municipal-admin
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev   # → http://localhost:5173
```
</details>

<details>
<summary><b>📱 Flutter App</b></summary>

```bash
cd frontend
flutter pub get
flutter run
```
</details>

<details>
<summary><b>🧠 Inference Service (Docker)</b></summary>

```bash
cd inference_service
docker build -t streetlight-infer .
docker run -p 7860:7860 \
  -e HF_REPO_ID=your/model-repo \
  -e HF_TOKEN=your_token \
  streetlight-infer
```
</details>

<details>
<summary><b>🔗 Smart Contract (already deployed — optional redeploy)</b></summary>

```bash
cd blockchain-layer
npm install && npx hardhat compile
npx hardhat ignition deploy ./ignition/modules/Lock.js --network sepolia
```
</details>

---

## Deployment

| Component | Platform | How |
|---|---|---|
| Backend API | Render.com | GitHub push → auto-deploy |
| Admin Portal | Vercel | GitHub push → auto-deploy |
| Inference Service | HuggingFace Spaces | Root `Dockerfile` → auto-build |
| Database | Supabase | Managed PostgreSQL |
| Blockchain | Ethereum Sepolia | Hardhat Ignition (one-time) |

## Screenshots

### 📱 Mobile App

| | | | | |
|:---:|:---:|:---:|:---:|:---:|
| ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot_20260513_073518.jpg.jpeg) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot_20260513_073702.jpg.jpeg) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot_20260513_073720.jpg.jpeg) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot_20260513_073732.jpg.jpeg) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot_20260513_073745.jpg.jpeg) |

### 🖥️ Web Dashboard

| | | |
|:---:|:---:|:---:|
| ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot%202026-05-16%20222724.png) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot%202026-05-16%20224451.png) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot%202026-05-16%20224513.png) |
| ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot%202026-05-16%20224541.png) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot%202026-05-16%20224703.png) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot%202026-05-16%20224802.png) |
| ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot%202026-05-16%20224821.png) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/Screenshot%202026-05-16%20224851.png) | ![](https://raw.githubusercontent.com/MQ-06/STREETLIGHT-PK/main/screenshots/livemap.png) |

---

---

## The Team

> *Built with late nights, chai, and a frustration with broken roads.*

| Name | Role |
|---|---|
| **Mariam Qadeem** | mariamqadeem181@gmail.com |
| **Areeba Tahir** | bitf22m011@pucit.edu.pk |
| **Kinzul Eman** | bitf22m015@pucit.edu.pk |
| **Shezonia Idrees** | bitf22m044@pucit.edu.pk |

---

<div align="center">

**StreetLight PK** — *Because no civic hazard should remain in the dark.*

[![Download App](https://img.shields.io/badge/🚀%20Download%20the%20App-streetlight--page.vercel.app-00C853?style=flat-square)](https://streetlight-page.vercel.app/)

🇵🇰 Made in Pakistan · PUCIT 2026

</div>
