import streamlit as st
import os
import json
import urllib.parse
import requests
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Setup Streamlit Config
st.set_page_config(page_title="Visual Novel Engine", layout="wide")
st.title("📖 AI Visual Novel Engine")

# Phase 1: Director's Cut (Caching, Sidebar, Session State)
@st.cache_resource
def get_groq_client():
    return Groq(api_key=os.environ.get("GROK_API_KEY"))

client = get_groq_client()

st.sidebar.header("Director's Configuration")
story_genre = st.sidebar.selectbox("Story Genre", ["Fantasy", "Sci-Fi", "Mystery", "Cyberpunk", "Horror"])
art_style = st.sidebar.selectbox("Art Style", ["Anime", "Realistic", "Watercolor", "Pixel Art", "Comic Book"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_scene" not in st.session_state:
    st.session_state.current_scene = None

# System Prompt to act as a structured JSON engine
SYSTEM_PROMPT = f"""
You are an expert interactive visual novel engine. 
The genre is {story_genre} and the visual art style is {art_style}.
You must respond strictly in JSON format matching the following structure:
{{
    "story_text": "The narrative paragraph describing the current scene and what is happening.",
    "image_prompt": "A highly detailed, comma-separated prompt describing the scene visually for an image generation model. Include the art style '{art_style}'.",
    "options": ["Choice 1", "Choice 2", "Choice 3"]
}}
Ensure the options are engaging actions the user can take. Always return valid JSON.
"""

def generate_scene(user_input):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add history
    for msg in st.session_state.chat_history:
        messages.append(msg)
        
    messages.append({"role": "user", "content": user_input})
    
    with st.spinner("Generating next scene..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            raw_content = response.choices[0].message.content
            
            # Phase 2: The Structured JSON Engine
            scene_data = json.loads(raw_content)
            
            # Save to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": raw_content})
            
            st.session_state.current_scene = scene_data
            st.rerun()
        except Exception as e:
            st.error(f"Error generating scene: {e}")

# Render Current Scene
if st.session_state.current_scene:
    scene = st.session_state.current_scene
    
    # Display story text
    st.markdown(f"### {scene.get('story_text', '')}")
    
    # Render Audio (Phase 4)
    # Using st.audio with the raw file data
    try:
        tts = gTTS(scene.get('story_text', ''), lang='en')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"Error generating TTS audio: {e}")
        
    # Phase 4 & 5: Render Visuals with Graceful Failures
    try:
        encoded_prompt = urllib.parse.quote(scene.get('image_prompt', ''))
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=512&nologo=true"
        
        headers = {"User-Agent": "VisualNovelEngine/1.0"}
        res = requests.get(url, headers=headers, timeout=15)
        
        if res.status_code == 200:
            st.image(res.content, use_container_width=True)
        else:
            st.toast("Image server is busy, skipping visual...")
    except Exception:
        st.toast("Image server timed out, skipping visual...")
        
    st.markdown("---")
    st.write("**What do you do next?**")
    
    # Phase 3: Dynamic UI Generation
    options = scene.get('options', [])
    for opt in options:
        if st.button(opt):
            generate_scene(opt)

else:
    # Start button
    if st.button("Start the Adventure", type="primary"):
        generate_scene("Begin the story.")