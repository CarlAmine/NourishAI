from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

# Setup app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model paths (download from Google Drive before running)
MODEL_DIR = "models"

# Load FAISS and data
print("📦 Loading index and data...")
index = faiss.read_index(f"{MODEL_DIR}/recipes_index.faiss")
with open(f"{MODEL_DIR}/recipes_data.pkl", "rb") as f:
    rag_texts = pickle.load(f)
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Model loaded.")

# Input format
class Query(BaseModel):
    ingredients: str

# Endpoint
@app.post("/suggest")
def suggest_recipe(query: Query):
    q_embed = model.encode([query.ingredients], convert_to_numpy=True)
    faiss.normalize_L2(q_embed)
    scores, ids = index.search(q_embed, k=3)

    results = []
    for i, idx in enumerate(ids[0]):
        recipe = rag_texts[idx]
        match = round(scores[0][i] * 100, 2)
        results.append(f"✅ Match: {match}%\n\n{recipe}")

    return {"recipe": "\n\n\n".join(results)}
