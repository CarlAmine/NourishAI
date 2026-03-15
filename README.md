# NourishAI

Production-style nutrition and recipe intelligence system with FAISS retrieval, metadata-aware filtering, grounded OpenAI outputs, and reproducible evaluation.

## RAG Setup
1. Build the index:
   `python scripts/build_rag_index.py --recipes data/sample_recipes.json --out-dir models/`
2. The index stores FAISS embeddings for each recipe title + ingredient list using `all-MiniLM-L6-v2`, plus a `recipe.pkl` payload.
3. Query it via `POST /api/v1/recipes/search` or `POST /api/v1/recipes/recommend`.

## OpenAI Setup (Phase 2)
1. Set `OPENAI_API_KEY` in `backend/.env` (see `backend/.env.example`).
2. Optionally set `OPENAI_MODEL`, `OPENAI_TEMPERATURE`, and `OPENAI_MAX_TOKENS`.
3. Optional: `OPENAI_TIMEOUT_SEC` controls request timeout, and `STRICT_STARTUP=true` fails boot if artifacts are missing.
4. Use grounded endpoints:
   - `POST /api/v1/recipes/recommend/grounded`
   - `POST /api/v1/meal-plans/generate`
   - `POST /api/v1/nutrition/qa`
Outputs are schema-validated and grounded in retrieved recipes.

## Current Retrieval Path
1. Normalize ingredients and query text.
2. Embed with `sentence-transformers/all-MiniLM-L6-v2`.
3. FAISS retrieves candidates by cosine similarity.
4. Apply metadata filters (cuisine, meal type, dietary tags, macros, time).
5. Optional lightweight reranking by ingredient overlap.

## Architecture (Current)

```
NourishAI/
  backend/
    app/
      api/
      core/
      repositories/
      schemas/
      services/
    requirements.txt
  data/
  eval/
  models/
  scripts/
  docker-compose.yml
```

### Retrieval Flow
1. User query hits `/api/v1/recipes/search` (or `/api/v1/recipes/recommend`).
2. Query is embedded with `sentence-transformers/all-MiniLM-L6-v2`.
3. FAISS retrieves candidate recipes with cosine similarity.
4. Optional metadata filters and lightweight reranking refine results.

### Grounded Recommendation Flow
1. Retrieve recipes with FAISS + filters.
2. Provide retrieved recipe context to the LLM.
3. Produce structured recommendations with source IDs/titles.

### Index Build Flow
1. Provide recipe JSON (see `data/sample_recipes.json`).
2. Run `python scripts/build_rag_index.py --recipes data/sample_recipes.json --out-dir models/`.
3. FAISS index + `recipe.pkl` are saved under `models/` for retrieval.

## Setup

### Local (Docker Compose)
```
docker compose up --build
```
This runs:
- FastAPI API on `http://localhost:8000`
- Streamlit on `http://localhost:8501`

## Verification (2026-03-15, Windows PowerShell)
Commands executed successfully:
```
python -m pip install -r backend\requirements.txt
```
```
$env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; python scripts\build_rag_index.py --recipes data\sample_recipes.json --out-dir models\
```
```
$env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; @'
import json
import threading
import time
import httpx
import uvicorn
from backend.app.main import app
HOST = "127.0.0.1"
PORT = 8005
BASE = f"http://{HOST}:{PORT}/api/v1"
config = uvicorn.Config(app, host=HOST, port=PORT, log_level="warning")
server = uvicorn.Server(config)
thread = threading.Thread(target=server.run, daemon=True)
thread.start()
for _ in range(30):
    try:
        httpx.get(f"{BASE}/health", timeout=1.0)
        break
    except Exception:
        time.sleep(0.2)
client = httpx.Client(timeout=10.0)
print(client.get(f"{BASE}/health").json())
print(client.get(f"{BASE}/ready").json())
print(client.post(f"{BASE}/recipes/search", json={
    "query": "high protein dinner with chicken and quinoa",
    "top_k": 3,
    "filters": {"meal_type": ["dinner"], "dietary_tags": ["high_protein"]},
    "include_diagnostics": True
}).json())
print(client.post(f"{BASE}/recipes/recommend/grounded", json={
    "ingredients": ["chicken", "garlic", "lemon"],
    "dietary_notes": "low carb",
    "top_k": 3,
    "include_diagnostics": True
}).json())
print(client.post(f"{BASE}/meal-plans/generate", json={
    "dietary_profile": "high protein",
    "calorie_target": 1800,
    "days": 2,
    "meals_per_day": 3
}).json())
print(client.post(f"{BASE}/nutrition/qa", json={
    "question": "Is quinoa a good source of protein?",
    "top_k": 3
}).json())
client.close()
server.should_exit = True
thread.join(timeout=5)
'@ | python -
```
```
$env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; python -m eval.runners.run_retrieval_eval
```
```
$env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; python -m eval.runners.run_generation_eval
```
```
python -m pytest backend\tests
```

### Legacy Ingestion (Optional)
The repo includes an older Qdrant-based ingestion prototype under `backend/app/ingestion`, but it is not used by the
current FAISS retrieval path. You can ignore it for the core workflow.

## Example Output

Request:
```json
{
  "query": "high protein dinner with chicken and quinoa",
  "top_k": 3,
  "filters": {
    "meal_type": ["dinner"],
    "dietary_tags": ["high_protein"]
  },
  "include_diagnostics": true
}
```

Response (truncated, verified 2026-03-15):
```json
{
  "results": [
    {
      "id": "rec-002",
      "title": "Lemon Garlic Chicken",
      "score": 0.28875704407691954,
      "dietary_tags": ["high_protein", "gluten_free", "low_carb"]
    }
  ],
  "diagnostics": {
    "candidate_k": 15,
    "reranked": true,
    "top_ids": ["rec-002", "rec-008", "rec-006"]
  }
}
```

### Grounded Recommendation Example
Request:
```json
{
  "ingredients": ["chicken", "garlic", "lemon"],
  "dietary_notes": "low carb",
  "top_k": 3,
  "include_diagnostics": true
}
```

Response (truncated, verified without `OPENAI_API_KEY`):
```json
{
  "recommended_recipes": [],
  "warnings": [
    "LLM generation failed; no grounded recommendations were returned."
  ],
  "source_recipes": [{ "id": "rec-002", "title": "Lemon Garlic Chicken" }]
}
```

### Meal Plan Example
Request:
```json
{
  "dietary_profile": "high protein",
  "calorie_target": 1800,
  "days": 2,
  "meals_per_day": 3
}
```

Response (truncated, verified without `OPENAI_API_KEY`):
```json
{
  "days": [],
  "warnings": [
    "LLM generation failed; no meal plan was returned."
  ],
  "source_recipes": [{ "id": "rec-002", "title": "Lemon Garlic Chicken" }]
}
```

## Evaluation Workflow (Phase 3)
1. Retrieval eval:
   `python -m eval.runners.run_retrieval_eval`
2. Grounded generation eval:
   `python -m eval.runners.run_generation_eval`
Metrics include hit@k (any expected ID retrieved), recall@k (fraction of expected IDs retrieved), filter/exclusion violations,
source-ID grounding checks, and fallback correctness. Generation eval runs a deterministic offline LLM by default; pass
`--mode openai` to call the live API.
Artifacts are saved to `eval/outputs/` as JSON and CSV (run metadata, summary metrics, per-case details).

Verified evaluation results (2026-03-15):
- Retrieval run: `eval/outputs/retrieval_eval_20260315_172249.json`
  Summary: baseline hit_rate=0.80, recall_avg=0.92, filter_violations=14, excluded_violations=8; filtered/reranked recall_avg=1.00 with zero violations.
- Generation run: `eval/outputs/generation_eval_20260315_172302.json`
  Summary: fallback_correct_rate=1.00, warning_correct_rate=1.00, source_id_violations=0, filter_violations=0.

## Observability & Health
- Structured JSON logs include request IDs, retrieval filters, rerank flags, top IDs, and latency per stage.
- Request ID is returned in `X-Request-ID`.
- Health endpoints:
  - `GET /api/v1/health` (basic liveness)
  - `GET /api/v1/ready` (index + OpenAI readiness)
  - `GET /api/v1/status` (alias of ready)
Example log (truncated):
```json
{"event":"rag_search","query":"chicken garlic lemon","strategy":"reranked","result_ids":["rec-002"],"timings_ms":{"total":12.4}}
```

## Troubleshooting
- `503 RAG index not available`: run `python scripts/build_rag_index.py --recipes data/sample_recipes.json --out-dir models/`.
- LLM endpoints warn when `OPENAI_API_KEY` is missing; retrieval still works.
- If `/ready` reports artifact mismatch, rebuild the FAISS index.
- In restricted network environments, set `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` to use cached model files.
- `python -m pytest backend/tests` may warn if pytest cannot write cache on Windows; tests still run.

## Resume Evidence
Implemented now:
- FAISS retrieval with metadata filters and lightweight reranking
- Structured LLM outputs grounded in retrieved recipes
- Reproducible eval scripts with JSON/CSV artifacts for retrieval + grounding
- Structured logging, request IDs, and health/ready endpoints

Planned next:
- Background ingestion jobs with status tracking
- Expanded test coverage and observability

## Notes
- The current recipe endpoint (`/api/v1/recipes/search`) deduplicates results at the recipe level.
