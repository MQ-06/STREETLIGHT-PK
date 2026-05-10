---
title: StreetLight Classifier
emoji: 🛣️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# StreetLight inference (remote Layer 1)

API: `GET /health`, `POST /predict` (multipart field **`file`**).

Set **Space secrets**: `HF_REPO_ID` (and `HF_TOKEN` if the model repo is private).  
Optional: `INFERENCE_API_TOKEN` — if set, clients must send `Authorization: Bearer <token>`.

See repository docs for wiring `AI_INFERENCE_URL` on Render.
