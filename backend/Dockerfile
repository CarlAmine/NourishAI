# ── Stage 1: Install Python deps ────────────────────────────────────────────
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
# pandas needed for the converter script
RUN pip install --no-cache-dir pandas

# ── Stage 2: Download Food.com dataset + build FAISS index ────────────────────
# Runs at BUILD time — artifacts are baked into the image.
# Requires KAGGLE_USERNAME + KAGGLE_KEY build args (set in Render Build Args).
FROM builder AS index-builder
WORKDIR /app

# Kaggle credentials passed as build args
ARG KAGGLE_USERNAME
ARG KAGGLE_KEY
# Number of recipes to index (50k is a good balance of coverage vs build time)
ARG RECIPE_LIMIT=50000

COPY scripts/ ./scripts/
COPY data/sample_recipes.json ./data/sample_recipes.json

RUN pip install --no-cache-dir kaggle

RUN mkdir -p /app/models /app/data && \
    if [ -n "${KAGGLE_USERNAME}" ] && [ -n "${KAGGLE_KEY}" ]; then \
        echo "==> Downloading Food.com dataset from Kaggle" && \
        mkdir -p /root/.config/kaggle && \
        echo "{\"username\":\"${KAGGLE_USERNAME}\",\"key\":\"${KAGGLE_KEY}\"}" > /root/.config/kaggle/kaggle.json && \
        chmod 600 /root/.config/kaggle/kaggle.json && \
        kaggle datasets download -d shuyangli94/food-com-recipes-and-user-interactions \
            --file RAW_recipes.csv \
            --path /tmp/foodcom \
            --unzip && \
        echo "==> Converting to NourishAI format (limit=${RECIPE_LIMIT})" && \
        python scripts/convert_foodcom.py \
            --input /tmp/foodcom/RAW_recipes.csv \
            --output /app/data/recipes.json \
            --limit ${RECIPE_LIMIT} && \
        echo "==> Building FAISS index" && \
        python scripts/build_rag_index.py \
            --recipes /app/data/recipes.json \
            --out-dir /app/models && \
        rm -rf /tmp/foodcom /root/.config/kaggle && \
        echo "==> Full dataset index built:" && ls -lh /app/models/ ; \
    else \
        echo "==> KAGGLE_USERNAME/KAGGLE_KEY not set, falling back to sample recipes" && \
        python scripts/build_rag_index.py \
            --recipes /app/data/sample_recipes.json \
            --out-dir /app/models && \
        echo "==> Sample index built (10 recipes):" && ls -lh /app/models/ ; \
    fi

# ── Stage 3: Runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy pre-built index
COPY --from=index-builder /app/models /app/models

# Copy application source
COPY . .

RUN mkdir -p /app/models /app/artifacts

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
