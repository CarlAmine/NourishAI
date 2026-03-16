# ── Stage 1: Install Python deps ─────────────────────────────────────────────
# This Dockerfile requires NO build context — everything is pulled from GitHub.
# Works regardless of what dockerContext is set to in Render dashboard.
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

# Clone the repo directly — no build context needed
ARG GIT_BRANCH=production
RUN git clone --depth=1 --branch=${GIT_BRANCH} \
    https://github.com/CarlAmine/NourishAI.git /src

# Install Python deps from the cloned repo
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /src/backend/requirements.txt && \
    pip install --no-cache-dir pandas kaggle

# ── Stage 2: Build FAISS index ───────────────────────────────────────────────
FROM builder AS index-builder
WORKDIR /app

ARG KAGGLE_USERNAME
ARG KAGGLE_KEY
ARG RECIPE_LIMIT=50000

RUN mkdir -p /app/models /app/data && \
    if [ -n "${KAGGLE_USERNAME}" ] && [ -n "${KAGGLE_KEY}" ]; then \
        echo "==> Kaggle credentials found — downloading Food.com dataset" && \
        mkdir -p /root/.config/kaggle && \
        echo "{\"username\":\"${KAGGLE_USERNAME}\",\"key\":\"${KAGGLE_KEY}\"}" > /root/.config/kaggle/kaggle.json && \
        chmod 600 /root/.config/kaggle/kaggle.json && \
        kaggle datasets download -d shuyangli94/food-com-recipes-and-user-interactions \
            --file RAW_recipes.csv \
            --path /tmp/foodcom \
            --unzip && \
        echo "==> Converting ${RECIPE_LIMIT} recipes" && \
        python /src/scripts/convert_foodcom.py \
            --input /tmp/foodcom/RAW_recipes.csv \
            --output /app/data/recipes.json \
            --limit ${RECIPE_LIMIT} && \
        echo "==> Building FAISS index" && \
        python /src/scripts/build_rag_index.py \
            --recipes /app/data/recipes.json \
            --out-dir /app/models && \
        rm -rf /tmp/foodcom /root/.config/kaggle && \
        echo "==> Done:" && ls -lh /app/models/ ; \
    else \
        echo "==> No Kaggle credentials — building from 10-recipe sample" && \
        python /src/scripts/build_rag_index.py \
            --recipes /src/data/sample_recipes.json \
            --out-dir /app/models && \
        echo "==> Sample index built:" && ls -lh /app/models/ ; \
    fi

# ── Stage 3: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Baked-in index artifacts
COPY --from=index-builder /app/models /app/models

# Pull app source from the cloned repo
COPY --from=builder /src/backend/ .

RUN mkdir -p /app/models /app/artifacts

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
