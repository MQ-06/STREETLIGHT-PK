# Hugging Face Space + monorepo: build from REPO ROOT (STREETLIGHT).
# HF clones your GitHub repo and runs `docker build` with context = repo root.
# Paths below are relative to that root.
#
# Local test:  docker build -t streetlight-infer .
# Local run:   docker run -p 7860:7860 -e HF_REPO_ID=your/model streetlight-infer

FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY inference_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY inference_service/model_loader.py inference_service/model_core.py inference_service/app.py ./

RUN mkdir -p models

ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
