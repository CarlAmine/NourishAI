# ── Stage 1: Install Python deps ────────────────────────────────────────────
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Download ML artifacts ──────────────────────────────────────────
# Runs at BUILD time — artifacts are baked into the image so startup is instant.
# Requires the Google Drive folder to be shared as "Anyone with the link".
FROM python:3.11-slim AS artifact-downloader
WORKDIR /app

RUN pip install --no-cache-dir "gdown>=4.7.3"

ARG GDRIVE_FOLDER_ID=10okoRXmRZDGtsF8e5cDxSLEzJWfuF9nl
ARG GDRIVE_FAISS_ID=
ARG GDRIVE_PKL_ID=

RUN mkdir -p /app/models && \
    echo "==> Downloading model folder (id=${GDRIVE_FOLDER_ID})" && \
    python - <<'EOF'
import os, sys, subprocess

folder_id = os.environ.get("GDRIVE_FOLDER_ID", "")
faiss_id  = os.environ.get("GDRIVE_FAISS_ID", "")
pkl_id    = os.environ.get("GDRIVE_PKL_ID", "")

def run(cmd):
    print("$", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0

ok = False

# Strategy 1: download entire folder
if folder_id:
    ok = run([
        "gdown", "--folder", folder_id,
        "--output", "/app/models",
        "--remaining-ok"
    ])

# Strategy 2: individual file IDs (set GDRIVE_FAISS_ID + GDRIVE_PKL_ID as build args)
if not ok and faiss_id and pkl_id:
    print("Folder download failed — trying individual file IDs")
    r1 = run(["gdown", faiss_id, "-O", "/app/models/faiss.index"])
    r2 = run(["gdown", pkl_id,   "-O", "/app/models/recipe.pkl"])
    ok = r1 and r2

if not ok:
    print("WARNING: artifact download failed — will retry at runtime startup")
    sys.exit(0)  # don't fail the build; lifespan.py will retry at runtime

# Verify
for name in ["faiss.index", "recipe.pkl"]:
    path = f"/app/models/{name}"
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  ✓ {name}: {size:,} bytes")
    else:
        print(f"  ✗ {name}: NOT FOUND")
EOF

# ── Stage 3: Runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy pre-downloaded artifacts (empty dir if download failed — runtime will retry)
COPY --from=artifact-downloader /app/models /app/models

COPY . .

RUN mkdir -p /app/models /app/artifacts

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
