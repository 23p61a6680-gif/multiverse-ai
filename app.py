import streamlit as st
import os
import json
import urllib.parse
import requests
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai
from gtts import gTTS
import base64
from io import BytesIO
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="AI Visual Novel Engine", page_icon="📖", layout="wide")

# ── Premium Storytelling CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;600&display=swap');

html, body, .stApp {
    background-color: #08090f;
    color: #ddd8c4;
    font-family: 'Lora', serif;
}

/* Starfield background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(99,60,180,.08) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(30,100,200,.06) 0%, transparent 55%),
        radial-gradient(ellipse at 60% 80%, rgba(180,60,100,.05) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

h1,h2,h3,h4 {
    font-family: 'Cinzel', serif;
    letter-spacing: .08em;
    color: #f0e6d2;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0f1a 0%, #0a0c16 100%) !important;
    border-right: 1px solid rgba(139,92,246,.2);
}
section[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif; }

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #4f3a8a, #7c3aed);
    color: #f0e6d2;
    border: 1px solid rgba(167,139,250,.3);
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    letter-spacing: .04em;
    transition: all .2s ease;
    box-shadow: 0 2px 8px rgba(124,58,237,.2);
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(124,58,237,.45);
    border-color: rgba(167,139,250,.6);
}

/* Scene image frame */
.scene-frame {
    border-radius: 12px;
    border: 1px solid rgba(167,139,250,.25);
    overflow: hidden;
    box-shadow: 0 8px 40px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.04);
    margin-bottom: 0;
}

/* Subtitle / story text */
.story-card {
    background: linear-gradient(135deg, rgba(15,10,30,.95), rgba(20,12,40,.95));
    border: 1px solid rgba(139,92,246,.3);
    border-radius: 12px;
    padding: 28px 36px;
    font-size: 1.12rem;
    line-height: 1.85;
    font-style: italic;
    color: #e8dfc8;
    margin: 18px 0 22px;
    box-shadow: 0 0 30px rgba(99,60,180,.15), inset 0 1px 0 rgba(255,255,255,.04);
    position: relative;
}
.story-card::before {
    content: '"';
    font-family: 'Cinzel', serif;
    font-size: 5rem;
    color: rgba(139,92,246,.18);
    position: absolute;
    top: -10px; left: 16px;
    line-height: 1;
}

/* Chapter badge */
.chapter-badge {
    display: inline-block;
    background: linear-gradient(135deg,#4f3a8a,#7c3aed);
    color: #f0e6d2;
    font-family: 'Cinzel', serif;
    font-size: .7rem;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 30px;
    margin-bottom: 10px;
    letter-spacing: .12em;
    box-shadow: 0 2px 10px rgba(124,58,237,.3);
}

/* Action choice buttons */
.choice-label {
    font-family: 'Cinzel', serif;
    font-size: .85rem;
    letter-spacing: .12em;
    color: #a78bfa;
    margin-bottom: 10px;
    text-transform: uppercase;
}

/* Text input */
.stTextInput>div>div>input {
    background: rgba(15,10,30,.8);
    color: #e8dfc8;
    border-radius: 8px;
    border: 1px solid rgba(139,92,246,.3);
    font-family: 'Lora', serif;
}
.stTextInput>div>div>input:focus {
    border-color: rgba(167,139,250,.6);
    box-shadow: 0 0 0 2px rgba(124,58,237,.15);
}

/* Metrics */
div[data-testid="metric-container"] {
    background: rgba(15,10,30,.6);
    border-radius: 8px;
    padding: 10px 14px;
    border: 1px solid rgba(139,92,246,.2);
}

/* Expander */
.stExpander { border: 1px solid rgba(139,92,246,.2) !important; border-radius: 10px; }

/* Divider */
hr { border-color: rgba(139,92,246,.15) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #08090f; }
::-webkit-scrollbar-thumb { background: rgba(124,58,237,.4); border-radius: 3px; }

/* Title glow */
.title-main {
    font-family: 'Cinzel', serif;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #c4b5fd, #f0e6d2, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: .1em;
    margin-bottom: 4px;
}
.title-sub {
    font-family: 'Inter', sans-serif;
    text-align: center;
    color: rgba(167,139,250,.6);
    font-size: .8rem;
    letter-spacing: .15em;
    text-transform: uppercase;
    margin-bottom: 28px;
}
</style>
""", unsafe_allow_html=True)

# ── Cached AI Clients ──────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    return Groq(api_key=os.environ.get("GROK_API_KEY"))

@st.cache_resource
def get_gemini_model():
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    return genai.GenerativeModel(
        "gemini-2.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )

# ── Session State ──────────────────────────────────────────────────────────────
for k, v in {
    "chat_history": [],
    "scene_store": [],
    "current_scene": None,
    "last_genre": "Fantasy",
    "last_art": "Cinematic",
    "turn": 0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎬 Director's Panel")
    if st.button("🆕 New Story", use_container_width=True):
        for k in ["chat_history", "scene_store", "current_scene", "turn"]:
            st.session_state[k] = [] if k in ("chat_history","scene_store") else (None if k=="current_scene" else 0)
        st.rerun()

    st.markdown("---")
    story_genre = st.selectbox("Genre", ["Fantasy","Sci-Fi","Mystery","Cyberpunk","Horror","Adventure","Romance"])
    art_style   = st.selectbox("Art Style", ["Cinematic","Anime","Realistic","Oil Painting","Watercolor","Pixel Art","Comic Book"])

    do_transition = False
    genre_changed = (story_genre != st.session_state.last_genre or art_style != st.session_state.last_art)
    if genre_changed and st.session_state.current_scene:
        st.warning("⚡ Settings changed — twist your story!")
        do_transition = st.button("Apply Genre Twist", use_container_width=True, type="primary")

    st.markdown("---")
    st.metric("Scenes Played", st.session_state.turn)
    st.metric("Chapters in History", max(0, len(st.session_state.scene_store) - 1))

# ── AI Scene Generator ─────────────────────────────────────────────────────────
def build_system_prompt(genre, art):
    return f"""You are a master storyteller and interactive visual novel AI engine.
Genre: {genre} | Visual Art Style: {art}

If the user message signals a genre/style change, weave an unexpected, dramatic plot twist seamlessly.
Write vivid, immersive narrative. Keep story_text under 60 words — punchy and cinematic.
Respond ONLY with valid JSON:
{{
  "story_text": "Vivid 2-3 sentence scene narrative. End with tension.",
  "image_prompt": "Hyper-detailed cinematic image prompt, {art} art style, dramatic lighting, highly detailed, 8k resolution.",
  "options": ["Compelling choice A","Compelling choice B","Compelling choice C"]
}}"""

def generate_scene(user_input, genre, art):
    sys_p = build_system_prompt(genre, art)
    messages = [{"role": "system", "content": sys_p}]
    messages += st.session_state.chat_history
    messages.append({"role": "user", "content": user_input})

    raw = ""
    with st.spinner("📜 Weaving your story…"):
        try:
            r = get_groq_client().chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.9,
            )
            raw = r.choices[0].message.content
        except Exception:
            st.toast("🔄 Switching to Gemini…")
            hist = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.chat_history)
            p = f"{sys_p}\n\nHistory:\n{hist}\nuser: {user_input}"
            raw = get_gemini_model().generate_content(p).text

    try:
        scene = json.loads(raw)
    except Exception:
        st.error("Invalid AI response. Please try again.")
        return

    # TTS audio
    audio_b64 = ""
    try:
        tts = gTTS(scene["story_text"], lang="en")
        buf = BytesIO(); tts.write_to_fp(buf); buf.seek(0)
        audio_b64 = base64.b64encode(buf.read()).decode()
    except Exception:
        pass

    # Pollinations image URL
    enc = urllib.parse.quote(scene.get("image_prompt", ""))
    img_url = f"https://image.pollinations.ai/prompt/{enc}?width=1280&height=640&nologo=true&seed={st.session_state.turn}"

    # Store clean history for AI
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": raw})

    # Store rich display data
    st.session_state.scene_store.append({
        "turn": st.session_state.turn + 1,
        "story_text": scene["story_text"],
        "image_url": img_url,
        "audio_b64": audio_b64,
        "genre": genre,
        "art": art,
    })

    st.session_state.current_scene = scene
    st.session_state.turn += 1
    st.session_state.last_genre = genre
    st.session_state.last_art = art
    if "custom_input" in st.session_state:
        st.session_state.custom_input = ""
    st.rerun()

# ── Handle transition ──────────────────────────────────────────────────────────
if do_transition:
    generate_scene(
        f"The world suddenly shifts — a dramatic {story_genre} transformation begins!",
        story_genre, art_style
    )

# ── Page Header ────────────────────────────────────────────────────────────────
st.markdown('<div class="title-main">AI Visual Novel Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="title-sub">✦ Multi-Modal Interactive Story Experience ✦</div>', unsafe_allow_html=True)

# ── Comic Book History ─────────────────────────────────────────────────────────
history = st.session_state.scene_store
if len(history) > 1:
    with st.expander(f"📚 Story Chronicle — {len(history)-1} Chapter(s)", expanded=False):
        for idx, s in enumerate(history[:-1]):
            left, right = st.columns([1, 1])
            if idx % 2 == 0:
                with left:
                    try: st.image(s["image_url"], use_container_width=True)
                    except: st.markdown("*(Image loading...)*")
                with right:
                    st.markdown(f'<span class="chapter-badge">Chapter {s["turn"]}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="story-card" style="font-size:.95rem;padding:18px 22px;">{s["story_text"]}</div>', unsafe_allow_html=True)
                    if s["audio_b64"]:
                        st.markdown(f'<audio src="data:audio/mp3;base64,{s["audio_b64"]}" controls style="width:100%;margin-top:8px;"></audio>', unsafe_allow_html=True)
            else:
                with left:
                    st.markdown(f'<span class="chapter-badge">Chapter {s["turn"]}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="story-card" style="font-size:.95rem;padding:18px 22px;">{s["story_text"]}</div>', unsafe_allow_html=True)
                    if s["audio_b64"]:
                        st.markdown(f'<audio src="data:audio/mp3;base64,{s["audio_b64"]}" controls style="width:100%;margin-top:8px;"></audio>', unsafe_allow_html=True)
                with right:
                    try: st.image(s["image_url"], use_container_width=True)
                    except: st.markdown("*(Image loading...)*")
            st.markdown("---")

# ── Current Scene ──────────────────────────────────────────────────────────────
scene = st.session_state.current_scene

if scene:
    # Scene image
    try:
        enc = urllib.parse.quote(scene.get("image_prompt", ""))
        img_url = f"https://image.pollinations.ai/prompt/{enc}?width=1280&height=640&nologo=true&seed={st.session_state.turn}"
        res = requests.get(img_url, headers={"User-Agent": "VisualNovelEngine/2.0"}, timeout=20)
        if res.status_code == 200:
            st.markdown('<div class="scene-frame">', unsafe_allow_html=True)
            st.image(res.content, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.toast("Image server busy — story continues!")
    except Exception:
        st.toast("Image timed out — story continues!")

    # Story text card
    st.markdown(f'<div class="story-card">{scene.get("story_text","")}</div>', unsafe_allow_html=True)

    # TTS autoplay
    try:
        tts = gTTS(scene["story_text"], lang="en")
        buf = BytesIO(); tts.write_to_fp(buf); buf.seek(0)
        st.audio(buf, format="audio/mp3", autoplay=True)
    except Exception:
        pass

    st.markdown("---")
    st.markdown('<div class="choice-label">⚔ Choose your path</div>', unsafe_allow_html=True)

    opts = scene.get("options", [])
    if opts:
        cols = st.columns(len(opts))
        for i, opt in enumerate(opts):
            if cols[i].button(f"↳ {opt}", use_container_width=True, key=f"opt_{st.session_state.turn}_{i}"):
                generate_scene(opt, story_genre, art_style)

    st.markdown("")
    with st.form("custom_form", clear_on_submit=True):
        c1, c2 = st.columns([4, 1])
        custom = c1.text_input("✏️ Write your own fate…", placeholder="I draw my sword and…", label_visibility="collapsed")
        submitted = c2.form_submit_button("→ Enter", type="primary", use_container_width=True)
        if submitted and custom.strip():
            generate_scene(custom, story_genre, art_style)

else:
    # ── Landing Screen ─────────────────────────────────────────────────────────
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding:40px 0;">
            <div style="font-size:4rem; margin-bottom:16px;">📖</div>
            <p style="font-family:'Lora',serif; font-size:1.1rem; color:#a78bfa; margin-bottom:8px;">
                A world of infinite stories awaits.
            </p>
            <p style="font-family:'Inter',sans-serif; font-size:.85rem; color:rgba(167,139,250,.5);">
                Configure your Genre & Art Style in the sidebar, then step into the unknown.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✦ Begin Your Adventure ✦", type="primary", use_container_width=True):
            generate_scene("Begin the story with a dramatic and immersive opening scene.", story_genre, art_style)