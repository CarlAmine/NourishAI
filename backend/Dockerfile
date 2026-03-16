# ── Stage 1: Install Python deps ────────────────────────────────────────────
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Download ML artifacts ──────────────────────────────────────────
# This runs at BUILD time so Render never needs to download at runtime.
# The image is larger but startup is instant and reliable.
FROM python:3.11-slim AS artifact-downloader
WORKDIR /app

RUN pip install --no-cache-dir gdown

# Build args — passed in by Render or via docker build --build-arg
ARG GDRIVE_FOLDER_ID=10okoRXmRZDGtsF8e5cDxSLEzJWfuF9nl

RUN mkdir -p /app/models && \
    echo "Downloading model artifacts from Google Drive folder ${GDRIVE_FOLDER_ID}" && \
    gdown --folder "https://drive.google.com/drive/folders/${GDRIVE_FOLDER_ID}" \
          --output /app/models \
          --no-cookies \
          --remaining-ok || \
    echo "WARNING: gdown folder download failed — artifacts will be downloaded at runtime"

# ── Stage 3: Runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy pre-downloaded artifacts from downloader stage
COPY --from=artifact-downloader /app/models /app/models

# Copy application source
COPY . .

RUN mkdir -p /app/models /app/artifacts

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
