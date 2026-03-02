import os
import json
import requests
import joblib
import numpy as np
import time
import streamlit as st
from streamlit_lottie import st_lottie
import pickle

category_dict = np.load('models/category_dict.npy', allow_pickle=True).item()

# -------------------------------
# 1. PAGE CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="NourishAI Pro | Chef System",
    page_icon="👨‍🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# 2. LOAD MODEL (CACHED)
# -------------------------------
import gdown

def load_recipe_csv():
    file_id = '1lE6zl-9dJKUnNu6CDuBvHPpGodKrGnoX'
    output = 'raw_recipes.npy'
    url = f'https://drive.google.com/uc?id={file_id}'

    if not os.path.exists(output):
        gdown.download(url, output, quiet=False)

    df = np.load('raw_recipes.npy', allow_pickle=True).item()
    return df
recipe_dict = load_recipe_csv()

import gdown
import os
import pickle
import streamlit as st
@st.cache_resource
def load_image_model():
    url = "https://github.com/CarlAmine/EECE-490/releases/download/v1.0/490Image.pkl"
    destination = "490Image.pkl"
    expected_size = 687 * 1024 * 1024  # 687 MB in bytes

    def download_file_stream(url, destination):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(destination, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    # Check if file is already good
    if not os.path.exists(destination) or os.path.getsize(destination) < expected_size:
        st.write("Downloading model file from GitHub...")
        try:
            download_file_stream(url, destination)
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")

    # Final size check
    if os.path.getsize(destination) < expected_size:
        raise ValueError("Downloaded file is too small. Possibly corrupted.")

    # Load model
    with open(destination, "rb") as f:
        model = pickle.load(f)

    return model


svc_model = load_image_model()

# -------------------------------
# 3. SESSION STATE
# -------------------------------
if 'generate_clicked' not in st.session_state:
    st.session_state.generate_clicked = False
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = ""

# -------------------------------
# 4. GLOBAL STYLING
# -------------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {
    --primary: #1E90FF;
    --bg: #FFFFFF;
    --card: #FFFFFF;
    --text: #1E90FF;
    --input: #FFFFFF;
    --border: #87CEFA;
}
body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Roboto', sans-serif;
}
.title-text {
    font-size: 6rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #2E3C49;
}
.subtitle-text {
    font-size: 2rem;
    font-weight: 500;
    margin-bottom: 2rem;
    color: #2E3C49;
}
div[data-testid="stTextArea"] label {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: #2E3C49 !important;
}
.stTextArea textarea {
    font-size: 1.6rem;
    padding: 1.5rem;
    background: var(--input);
    border: 2px solid var(--border);
    border-radius: 12px;
    min-height: 200px;
    color: var(--text);
}
.stButton>button {
    font-size: 1.6rem;
    padding: 1rem 2rem;
    background: var(--primary);
    color: #FFF;
    border: none;
    border-radius: 12px;
    margin-top: 1.5rem;
    width: 100%;
}
.stButton>button:hover {
    background: #1A7AD9;
}
.recipe-card {
    background: var(--card);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 2px solid var(--border);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    color: var(--text);
}
.recipe-card h3 {
    font-size: 1.6rem;
    margin-bottom: 1rem;
    color: var(--text);
}
.big-text {
    font-size: 1.4rem;
    line-height: 1.6;
    color: var(--text);
}
.photo-container {
    width: 100%;
    padding-top: 100%;
    position: relative;
    margin: 0 auto;
}
.photo-container img {
    position: absolute;
    top: 0; left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 12px;
    border: 2px solid var(--border);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 5. HEADER
# -------------------------------
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h1 class="title-text">NOURISH AI</h1>
    <p class="subtitle-text">Professional Recipe Generator</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# 6. HELPER FUNCTIONS
# -------------------------------
from PIL import Image
import numpy as np
import io
import re

def preprocess_for_svc(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((15, 15))
    img_array = np.array(img) / 255.0
    flat_array = img_array.flatten().reshape(1, -1)
    return flat_array

def format_nutrition(nutrition_data):
    nutrition_str = str(nutrition_data)
    cleaned = re.sub(r'[^\d.,]', '', nutrition_str)
    number_strings = [s for s in cleaned.split(',') if s]
    numbers = []
    for num_str in number_strings:
        try:
            numbers.append(float(num_str))
        except ValueError:
            continue
    labels = ['Calories', 'total fat', 'total sugar', 'sodium', 'protein', 'saturated fat']
    nutrition_dict = {}
    if len(numbers) >= 6:
        indices = [0, 1, 2, 3, 4, 6] if len(numbers) == 7 else range(6)
        for i, label in enumerate(labels):
            try:
                nutrition_dict[label] = numbers[indices[i]]
            except (IndexError, KeyError):
                nutrition_dict[label] = None
    else:
        nutrition_dict = {label: None for label in labels}
    return nutrition_dict

def get_recipe_attributes(name):
    target = name.lower()
    matching_indices = [
        index 
        for index, recipe_name in recipe_dict['name'].items() 
        if target in recipe_name.lower()
    ]
    if not matching_indices:
        return {"error": "No recipe found with that name"}
    first_match_index = matching_indices[0]
    return {
        'minutes': recipe_dict['minutes'][first_match_index],
        'ingredients': recipe_dict['ingredients'][first_match_index],
        'steps': recipe_dict['steps'][first_match_index],
        'nutrition': recipe_dict['nutrition'][first_match_index]
    }

def format_ingredients(raw_ingredients):
    ingredients_str = ''.join(raw_ingredients)
    return [ing.strip(" '\"") for ing in ingredients_str.split(',') if ing.strip()]

def load_lottie_file(filename):
    path = os.path.join(os.path.dirname(__file__), '..', 'assets', filename)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return None
    return None

lottie_data = load_lottie_file("Animation.json")
lottie_data_2 = load_lottie_file("Animation1.json")

# -------------------------------
# 7. SHOW LOTTIE ANIMATION
# -------------------------------
def show_lottie_animation(animation_data, speed=1, height=300, width=300, key_suffix=""):
    if animation_data:
        st.markdown(
            f"""<div style="background-color:#FFFFFF; padding:1rem; border-radius:12px; text-align:center;">""",
            unsafe_allow_html=True
        )
        st_lottie(
            animation_data,
            speed=speed,
            reverse=False,
            loop=True,
            quality="high",
            height=height,
            width=width,
            key=f"anim_{key_suffix}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# 8. LAYOUT
# -------------------------------
col_input, col_anim, col_output = st.columns([1, 0.8, 1])

with col_input:
    uploaded_file = st.file_uploader("OR Upload an Image of the Dish:", type=["jpg", "jpeg", "png"], key="image_upload")
    image_urls = [
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd",
        "https://images.unsplash.com/photo-1490645935967-10de6ba17061",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836"
    ]
    for i in range(0, 4, 2):
        row = st.columns(2)
        for j in range(2):
            with row[j]:
                st.markdown(f"""
                <div class="photo-container">
                    <img src="{image_urls[i + j]}" alt="Photo {i + j + 1}">
                </div>
                """, unsafe_allow_html=True)

with col_anim:
    if st.session_state.generate_clicked and lottie_data:
        show_lottie_animation(lottie_data, key_suffix="1")
    if st.session_state.generate_clicked and lottie_data_2:
        show_lottie_animation(lottie_data_2, key_suffix="2")

with col_output:
    if uploaded_file is not None:
        try:
            with st.spinner("Analyzing image and identifying dish..."):
                img_array = preprocess_for_svc(uploaded_file.read())
                prediction = svc_model.predict(img_array)
                predicted_class = category_dict[prediction[0]]
                predicted_class = predicted_class.replace('_',' ')
                st.markdown(f"""
                <div class="recipe-card">
                    <h3>📷 Dish Identified from Image</h3>
                    <p class="big-text">🍽️ <strong>{predicted_class}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                recipe_data = get_recipe_attributes(predicted_class)
                if 'error' not in recipe_data:
                    ingredients = format_ingredients(recipe_data['ingredients'])
                    steps = ''.join([step.strip("'") for step in recipe_data['steps']])
                    nutrition = format_nutrition(recipe_data['nutrition'])
                    st.markdown(f"""
                    <div class="recipe-card">
                        <h3>📝 Recipe Details</h3>
                        <p>⏱ Cooking Time: <strong>{recipe_data['minutes']} minutes</strong></p>
                        <p>🥕 Ingredients: <strong>{ingredients}</strong></p>
                        <pre>👩‍🍳 Steps:\n{steps}</pre>
                        <pre>📊 Nutrition:\n{nutrition}</pre>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"No recipe found for {predicted_class}", icon="⚠️")
        except Exception as e:
            st.error(f"Error: {str(e)}", icon="🛑")

# -------------------------------
# 9. SUPPRESS TENSORFLOW WARNINGS
# -------------------------------
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
