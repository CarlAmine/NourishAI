# 🌿 NourishAI

AI-powered recipe generation — identify dishes from ingredients or photos using ML models and a Streamlit interface.

## 📁 Project Structure

```
NourishAI/
├── app/
│   └── app.py                   # Main Streamlit frontend application
├── backend/
│   └── main.py                  # FastAPI backend for RAG-based recipe search
├── notebooks/
│   ├── 490EDA.ipynb             # Exploratory Data Analysis
│   ├── 490Image.ipynb           # Image model training
│   ├── build_index.ipynb        # FAISS index construction
│   └── demo_RAG.ipynb           # RAG pipeline demo
├── templates/
│   └── index.html               # HTML frontend template
├── assets/
│   ├── Animation.json           # Lottie animation 1
│   └── Animation1.json          # Lottie animation 2
├── config/
│   └── .streamlit/config.toml  # Streamlit configuration
├── .devcontainer/
│   └── devcontainer.json        # GitHub Codespaces config
├── .github/
│   └── workflows/
│       └── docker-image.yml     # Docker CI/CD workflow
├── DockerFile                   # Docker build instructions
└── requirements.txt             # Python dependencies
```

## 🚀 Features

- **Image-Based Recipe Detection**: Upload a food photo → get the dish name + full recipe
- **Ingredient-Based Recipe Search**: Enter ingredients → retrieve matching recipes via FAISS
- **RAG Pipeline**: Semantic search using `all-MiniLM-L6-v2` + FAISS index
- **Lottie Animations**: Smooth animated feedback during processing

## ⚙️ Setup & Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app/app.py

# Run the FastAPI backend (optional)
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## 🔗 Model Downloads

| Asset | Link |
|---|---|
| FAISS Index + recipe.pkl | [Google Drive](https://drive.google.com/drive/folders/10okoRXmRZDGtsF8e5cDxSLEzJWfuF9nl?usp=sharing) |
| Image Model (490Image.pkl) | [Google Drive](https://drive.google.com/file/d/1kyATzxBuLP5nWScPpwT9KrkkIuxY22vX/view?usp=sharing) |

## 🐳 Docker

```bash
docker pull carlamine/nourishai-app:latest
docker run carlamine/nourishai-app:latest
```
