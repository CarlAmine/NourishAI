# 🥗 NourishAI

An AI-powered recipe recommendation system that identifies dishes from ingredients or food images.

## 📁 Project Structure

```
NourishAI/
├── app/                    # Application source code
│   ├── app.py              # Streamlit frontend & main app logic
│   └── api.py              # FastAPI backend (RAG-based recipe search)
├── notebooks/              # Jupyter notebooks for EDA & model training
│   ├── EDA.ipynb           # Exploratory Data Analysis
│   ├── ImageModel.ipynb    # Image classification model
│   ├── build_index.ipynb   # FAISS index builder
│   └── demo_RAG.ipynb      # RAG demo notebook
├── assets/                 # Static assets
│   ├── Animation.json      # Lottie animation 1
│   ├── Animation1.json     # Lottie animation 2
│   └── recipe1.jpg         # Sample recipe image
├── models/                 # ML model artifacts
│   └── category_dict.npy   # Category dictionary for image classifier
├── templates/              # HTML templates
│   └── index.html          # Recipe predictor UI
├── config/                 # Configuration files
│   ├── .streamlit/
│   │   └── config.toml
│   └── .devcontainer/
│       └── devcontainer.json
├── docs/                   # Documentation & presentations
│   └── NourishAI_Presentation.pptx
├── .github/workflows/      # CI/CD workflows
│   └── docker-image.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Run Locally
```bash
pip install -r requirements.txt
streamlit run app/app.py
```

### Run with Docker
```bash
docker pull carlamine/nourishai-app:latest
docker run -p 8501:8501 carlamine/nourishai-app:latest
```

## 🧠 Models

This project uses two main models:

1. **Ingredient-based Recipe Recommender** — Uses FAISS + RAG to recommend recipes from a comma-separated ingredient list.
2. **Image-based Recipe Identifier** — An SVC model trained to classify food images and match them to recipes.

### Model Downloads (Google Drive)
- [FAISS index + recipe.pkl](https://drive.google.com/drive/folders/10okoRXmRZDGtsF8e5cDxSLEzJWfuF9nl?usp=sharing)
- [Image model (490Image.pkl)](https://github.com/CarlAmine/EECE-490/releases/download/v1.0/490Image.pkl)
