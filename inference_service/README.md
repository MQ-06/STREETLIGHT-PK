# StreetLight inference (remote Layer 1)

**Hugging Face Space (monorepo):** HF reads **`README.md` and `Dockerfile` at the repository root** — see the project root `README.md` (YAML + docker) and root `Dockerfile`.

This folder holds the Python app copied into the image: `app.py`, `model_core.py`, `model_loader.py`, `requirements.txt`.

API: `GET /health`, `POST /predict` (multipart field **`file`**).

**Space secrets:** `HF_REPO_ID` (and `HF_TOKEN` if the model repo is private). Optional `INFERENCE_API_TOKEN` for `Authorization: Bearer …` on `/predict`.

**Standalone deploy:** use `Dockerfile.slim` with build context = this directory only (no monorepo).
