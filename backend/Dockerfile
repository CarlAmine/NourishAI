# ── Stage 1: Install Python deps ────────────────────────────────────────────
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Build RAG index from bundled recipes JSON ─────────────────────
# Runs at BUILD time — no Google Drive needed, fully self-contained.
# Replace data/sample_recipes.json with your full dataset to get better results.
FROM builder AS index-builder
WORKDIR /app

COPY data/sample_recipes.json ./data/sample_recipes.json
COPY scripts/build_rag_index.py ./scripts/build_rag_index.py

RUN mkdir -p /app/models && \
    echo "==> Building FAISS index from data/sample_recipes.json" && \
    python scripts/build_rag_index.py \
        --recipes data/sample_recipes.json \
        --out-dir models && \
    echo "==> Index build complete:" && \
    ls -lh models/

# ── Stage 3: Runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy pre-built index artifacts
COPY --from=index-builder /app/models /app/models

# Copy application source
COPY . .

RUN mkdir -p /app/models /app/artifacts

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
