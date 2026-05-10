---
title: StreetLight Classifier
emoji: 🛣️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# StreetLight inference (remote Layer 1)

**API:** `GET /health`, `POST /predict` (multipart form field **`file`**).

**Secrets** (Space → Settings → Secrets): `HF_REPO_ID` (e.g. `MQ-06/streetlight-model`), optional `HF_TOKEN`, optional `INFERENCE_API_TOKEN`.

**Render:** set `AI_INFERENCE_URL` to this Space URL and `SKIP_LAYER1_MODEL=true`.
