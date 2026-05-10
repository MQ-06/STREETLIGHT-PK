---
title: StreetLight Classifier (HF Space)
emoji: 🛣️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# StreetLight (monorepo)

This repository contains the full **StreetLight** project. The **Hugging Face Space** uses the **`Dockerfile` in this root directory**, which copies files from **`inference_service/`** and runs the remote classifier on port **7860**.

- Inference API: `GET /health`, `POST /predict` (multipart field **`file`**).
- Space secrets: set **`HF_REPO_ID`** (and **`HF_TOKEN`** if the model repo is private). Optional **`INFERENCE_API_TOKEN`** for `Authorization: Bearer …` on `/predict`.
- Main backend (Render): set **`AI_INFERENCE_URL`** to your Space URL (see `inference_service/README.md`).
