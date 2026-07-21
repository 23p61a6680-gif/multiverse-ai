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

load_dotenv()

st.set_page_config(page_title="AI Visual Novel Engine", page_icon="📖", layout="wide")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;600&display=swap');

html, body, .stApp {
    background-color: #08090f;
    color: #ddd8c4;
    font-family: 'Lora', serif;
}
.stApp::before {
    content: '';
    position: fixed; top:0; left:0; right:0; bottom:0;
    background: radial-gradient(ellipse at 20% 50%, rgba(99,60,180,.09) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(30,100,200,.06) 0%, transparent 55%);
    pointer-events: none; z-index: 0;
}
h1,h2,h3,h4 { font-family:'Cinzel',serif; letter-spacing:.08em; color:#f0e6d2; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0d0f1a,#0a0c16) !important;
    border-right: 1px solid rgba(139,92,246,.2);
}
section[data-testid="stSidebar"] * { font-family:'Inter',sans-serif; }
.stButton>button {
    background: linear-gradient(135deg,#4f3a8a,#7c3aed);
    color: #f0e6d2; border: 1px solid rgba(167,139,250,.3);
    border-radius: 6px; font-family:'Inter',sans-serif;
    font-weight:600; letter-spacing:.04em;
    transition: all .2s ease; box-shadow:0 2px 8px rgba(124,58,237,.2);
}
.stButton>button:hover {
    transform:translateY(-2px);
    box-shadow:0 6px 20px rgba(124,58,237,.45);
    border-color:rgba(167,139,250,.6);
}
.story-card {
    background: linear-gradient(135deg,rgba(15,10,30,.95),rgba(20,12,40,.95));
    border: 2px solid rgba(139,92,246,.4);
    border-radius: 12px; padding: 26px 34px;
    font-size: 1.12rem; line-height: 1.85;
    font-style: italic; color: #e8dfc8;
    margin: 18px 0 22px;
    box-shadow: 0 0 30px rgba(99,60,180,.2), inset 0 1px 0 rgba(255,255,255,.04);
    position: relative;
}
.story-card::before {
    content: '"'; font-family:'Cinzel',serif;
    font-size:5rem; color:rgba(139,92,246,.18);
    position:absolute; top:-10px; left:16px; line-height:1;
}
.chapter-badge {
    display:inline-block;
    background:linear-gradient(135deg,#4f3a8a,#7c3aed);
    color:#f0e6d2; font-family:'Cinzel',serif;
    font-size:.7rem; font-weight:700;
    padding:4px 14px; border-radius:30px;
    margin-bottom:10px; letter-spacing:.12em;
}
.title-main {
    font-family:'Cinzel',serif; font-size:2.4rem; font-weight:700;
    background:linear-gradient(135deg,#c4b5fd,#f0e6d2,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    text-align:center; letter-spacing:.1em; margin-bottom:4px;
}
.title-sub {
    font-family:'Inter',sans-serif; text-align:center;
    color:rgba(167,139,250,.6); font-size:.8rem;
    letter-spacing:.15em; text-transform:uppercase; margin-bottom:28px;
}
.choice-label {
    font-family:'Cinzel',serif; font-size:.85rem;
    letter-spacing:.12em; color:#a78bfa; margin-bottom:10px;
    text-transform:uppercase;
}
.stTextInput>div>div>input {
    background:rgba(15,10,30,.8); color:#e8dfc8;
    border-radius:8px; border:1px solid rgba(139,92,246,.3);
    font-family:'Lora',serif;
}
div[data-testid="metric-container"] {
    background:rgba(15,10,30,.6); border-radius:8px;
    padding:10px 14px; border:1px solid rgba(139,92,246,.2);
}
.stExpander { border:1px solid rgba(139,92,246,.2) !important; border-radius:10px; }
hr { border-color:rgba(139,92,246,.15) !important; }
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:#08090f; }
::-webkit-scrollbar-thumb { background:rgba(124,58,237,.4); border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ── Cached AI clients ──────────────────────────────────────────────────────────
@st.cache_resource
def get_groq():
    return Groq(api_key=os.environ.get("GROK_API_KEY", ""))

@st.cache_resource
def get_gemini():
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
    return genai.GenerativeModel(
        "gemini-2.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "chat_history": [],    # clean {role, content} for AI context
    "scene_store":  [],    # rich {story_text, image_url, audio_b64} per scene
    "current_scene": None, # parsed JSON dict of latest scene
    "show_history":  False,
    "turn": 0,
    "last_genre": "Fantasy",
    "last_art": "Cinematic",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helper: generate one scene ─────────────────────────────────────────────────
def build_prompt(genre, art):
    return f"""You are a master storytelling AI for an interactive visual novel.
Genre: {genre} | Art Style: {art}
If the user message signals a genre/style switch, write a dramatic plot twist that transitions the story.
Respond ONLY with a valid JSON object with EXACTLY these keys:
{{
  "story_text": "2-3 vivid, immersive sentences. End with tension or a cliffhanger.",
  "image_prompt": "Detailed scene description for image generation, {art} style, dramatic lighting, ultra-detailed.",
  "options": ["Action A", "Action B", "Action C"]
}}"""

def fetch_image(prompt_text):
    """Returns image bytes or None."""
    enc = urllib.parse.quote(prompt_text)
    url = f"https://image.pollinations.ai/prompt/{enc}?width=1280&height=640&nologo=true&seed={st.session_state.turn}"
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None

def make_audio_b64(text):
    try:
        tts = gTTS(text, lang="en")
        buf = BytesIO(); tts.write_to_fp(buf); buf.seek(0)
        return base64.b64encode(buf.read()).decode()
    except Exception:
        return ""

def generate_scene(user_input, genre, art):
    sys_p = build_prompt(genre, art)
    messages = [{"role": "system", "content": sys_p}]
    messages += st.session_state.chat_history
    messages.append({"role": "user", "content": user_input})

    raw = ""
    with st.spinner("📜 Weaving your story…"):
        # Primary: Groq
        try:
            r = get_groq().chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.9,
            )
            raw = r.choices[0].message.content
        except Exception:
            st.toast("🔄 Switching to Gemini…")
            try:
                hist = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.chat_history)
                p = f"{sys_p}\n\nHistory:\n{hist}\nuser: {user_input}"
                raw = get_gemini().generate_content(p).text
            except Exception as e:
                st.error(f"Both AIs failed: {e}")
                return

    try:
        scene = json.loads(raw)
    except Exception:
        st.error("AI returned invalid response. Please try again.")
        return

    story_text  = scene.get("story_text", "")
    img_prompt  = scene.get("image_prompt", "")
    options     = scene.get("options", [])

    # Image (Pollinations)
    img_bytes = None
    with st.spinner("🎨 Painting the scene…"):
        img_bytes = fetch_image(img_prompt)
    if img_bytes is None:
        st.toast("Image server busy – story continues!")

    # Image URL for history (stored as URL, re-fetched if needed)
    enc = urllib.parse.quote(img_prompt)
    img_url = f"https://image.pollinations.ai/prompt/{enc}?width=1280&height=640&nologo=true&seed={st.session_state.turn}"

    # TTS
    audio_b64 = make_audio_b64(story_text)

    # Save clean history for AI (no image/audio blobs)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": raw})

    # Save rich scene for display
    st.session_state.scene_store.append({
        "turn":       st.session_state.turn + 1,
        "story_text": story_text,
        "img_bytes":  img_bytes,   # bytes for instant display
        "img_url":    img_url,     # URL fallback for history
        "audio_b64":  audio_b64,
        "options":    options,
        "genre":      genre,
        "art":        art,
    })

    st.session_state.current_scene = scene
    st.session_state.turn += 1
    st.session_state.last_genre = genre
    st.session_state.last_art   = art
    st.rerun()

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎬 Director's Panel")

    if st.button("🆕 New Story", use_container_width=True):
        st.session_state.chat_history  = []
        st.session_state.scene_store   = []
        st.session_state.current_scene = None
        st.session_state.show_history  = False
        st.session_state.turn          = 0
        st.rerun()

    st.markdown("---")
    story_genre = st.selectbox("Genre", ["Fantasy","Sci-Fi","Mystery","Cyberpunk","Horror","Adventure","Romance"])
    art_style   = st.selectbox("Art Style", ["Cinematic","Anime","Realistic","Oil Painting","Watercolor","Pixel Art","Comic Book"])

    # History toggle
    if st.session_state.scene_store:
        hist_label = "📚 Hide History" if st.session_state.show_history else "📚 Show History"
        if st.button(hist_label, use_container_width=True):
            st.session_state.show_history = not st.session_state.show_history
            st.rerun()

    # Genre twist button — only when settings changed mid-story
    genre_changed = (story_genre != st.session_state.last_genre or art_style != st.session_state.last_art)
    do_transition = False
    if genre_changed and st.session_state.current_scene:
        st.warning("⚡ Settings changed! Apply a genre twist.")
        do_transition = st.button("Apply Genre Twist", use_container_width=True, type="primary")

    st.markdown("---")
    st.metric("Scenes Played", st.session_state.turn)
    st.metric("Chapters", max(0, len(st.session_state.scene_store)))

# ── Handle genre transition ────────────────────────────────────────────────────
if do_transition:
    generate_scene(
        f"Suddenly the world shifts — a dramatic {story_genre} transformation sweeps through!",
        story_genre, art_style
    )

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="title-main">AI Visual Novel Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="title-sub">✦ Multi-Modal Interactive Story — Groq · Gemini · Pollinations · gTTS ✦</div>', unsafe_allow_html=True)

# ── COMIC BOOK HISTORY ─────────────────────────────────────────────────────────
if st.session_state.show_history and st.session_state.scene_store:
    st.markdown("---")
    st.markdown("## 📚 Story Chronicle")
    chapters = st.session_state.scene_store[:-1]  # all except the latest (shown below)
    if not chapters:
        st.info("More scenes needed for history. Keep playing!")
    for idx, s in enumerate(chapters):
        left, right = st.columns([1, 1])
        if idx % 2 == 0:
            with left:
                if s.get("img_bytes"):
                    st.image(s["img_bytes"], use_container_width=True)
                else:
                    st.image(s["img_url"], use_container_width=True)
            with right:
                st.markdown(f'<span class="chapter-badge">Chapter {s["turn"]}</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="story-card" style="font-size:.95rem;padding:18px 22px;">{s["story_text"]}</div>', unsafe_allow_html=True)
                if s.get("audio_b64"):
                    st.markdown(f'<audio src="data:audio/mp3;base64,{s["audio_b64"]}" controls style="width:100%;margin-top:8px;"></audio>', unsafe_allow_html=True)
        else:
            with left:
                st.markdown(f'<span class="chapter-badge">Chapter {s["turn"]}</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="story-card" style="font-size:.95rem;padding:18px 22px;">{s["story_text"]}</div>', unsafe_allow_html=True)
                if s.get("audio_b64"):
                    st.markdown(f'<audio src="data:audio/mp3;base64,{s["audio_b64"]}" controls style="width:100%;margin-top:8px;"></audio>', unsafe_allow_html=True)
            with right:
                if s.get("img_bytes"):
                    st.image(s["img_bytes"], use_container_width=True)
                else:
                    st.image(s["img_url"], use_container_width=True)
        st.markdown("---")

# ── CURRENT SCENE ──────────────────────────────────────────────────────────────
scene = st.session_state.current_scene

if scene:
    # Get the latest stored scene (has img_bytes)
    latest = st.session_state.scene_store[-1] if st.session_state.scene_store else {}

    # Image — use cached bytes first, then URL fallback
    if latest.get("img_bytes"):
        st.image(latest["img_bytes"], use_container_width=True)
    elif latest.get("img_url"):
        try:
            st.image(latest["img_url"], use_container_width=True)
        except Exception:
            st.toast("Image unavailable – story continues!")

    # Story text card
    st.markdown(f'<div class="story-card">{scene.get("story_text","")}</div>', unsafe_allow_html=True)

    # TTS autoplay
    if latest.get("audio_b64"):
        st.markdown(
            f'<audio src="data:audio/mp3;base64,{latest["audio_b64"]}" autoplay style="display:none;"></audio>',
            unsafe_allow_html=True
        )
        # Also show visible player
        st.markdown(
            f'<audio src="data:audio/mp3;base64,{latest["audio_b64"]}" controls style="width:100%;margin-bottom:12px;"></audio>',
            unsafe_allow_html=True
        )

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
        custom = c1.text_input("✏️ Write your own fate…", placeholder="I draw my sword and charge…", label_visibility="collapsed")
        if c2.form_submit_button("→ Go", type="primary", use_container_width=True):
            if custom.strip():
                generate_scene(custom, story_genre, art_style)

else:
    # ── LANDING SCREEN ─────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:48px 0;">
            <div style="font-size:4.5rem;margin-bottom:20px;">📖</div>
            <p style="font-family:'Lora',serif;font-size:1.1rem;color:#a78bfa;margin-bottom:10px;">
                A world of infinite stories awaits.
            </p>
            <p style="font-family:'Inter',sans-serif;font-size:.85rem;color:rgba(167,139,250,.5);">
                Set your Genre &amp; Art Style in the sidebar, then step into the unknown.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✦ Begin Your Adventure ✦", type="primary", use_container_width=True):
            generate_scene("Begin the story with a dramatic and immersive opening scene.", story_genre, art_style)