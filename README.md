# 🎬 [AI Visual Novel Engine — Watch the Demo](https://drive.google.com/drive/folders/11uDepNIVG0h5nenIxFTEtgV0iyPv6M0w?usp=sharing)

> **A multi-modal, AI-powered "Choose Your Own Adventure" Visual Novel built with Python & Streamlit.**  
> MirAI School of Technology — Virtual Summer Internship 2026 · AI Builder Track · Capstone Project

---

## 📽️ [▶ Click Here to Watch the Demo](https://drive.google.com/drive/folders/11uDepNIVG0h5nenIxFTEtgV0iyPv6M0w?usp=sharing)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Dual AI Engine** | Groq (Llama 3.3 70B) as primary, auto-falls back to Gemini 2.5 Flash on rate-limit |
| 📜 **Structured JSON Engine** | AI returns strict JSON: `story_text`, `image_prompt`, `options` |
| 🎮 **Dynamic Choice Buttons** | Buttons are generated at runtime from the AI's response — no hardcoded UI |
| 🖼️ **AI Scene Images** | Every scene generates a contextual image via **Pollinations.ai** (zero token cost) |
| 🔊 **TTS Narration** | Story text auto-narrated using **gTTS**, plays directly in the browser |
| 📚 **Comic Book History** | Sidebar toggle reveals alternating image/text comic book layout of all chapters |
| ⚡ **Genre Twist** | Change genre mid-game → AI writes a dramatic plot transition |
| 🛡️ **Graceful Failures** | All API calls wrapped in `try/except` — app never crashes on network errors |
| 🎨 **Premium Storytelling UI** | Cinzel + Lora fonts, glowing story cards, cinematic scene frames, dark mode |

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌──────────────────────────────────────┐
│   Groq API  (Primary — Fast & Free)  │
│   Model: llama-3.3-70b-versatile     │
│   JSON Mode: response_format         │
└──────────────┬───────────────────────┘
               │  on rate-limit / error
               ▼
┌──────────────────────────────────────┐
│   Gemini 2.5 Flash  (Fallback)       │
│   JSON Mode: response_mime_type      │
└──────────────┬───────────────────────┘
               │
               ▼
        json.loads(raw)
               │
      ┌────────┴─────────┐
      │                  │
      ▼                  ▼
Pollinations.ai        gTTS
 (Scene Image)      (MP3 Audio)
      │                  │
      └────────┬─────────┘
               ▼
      Streamlit UI Render
   Image → Story Card → Choices
```

### Key Engineering Concepts
- **`@st.cache_resource`** — AI clients instantiated once and reused across sessions
- **Dual session stores** — `chat_history` (clean role/content for AI context) + `scene_store` (rich image bytes, audio, text for UI)
- **`try/except` fallback chain** — Groq → Gemini → graceful `st.toast()` notification
- **Dynamic button loop** — `for opt in options: st.button(opt)` generates the entire choice UI at runtime

---

## 🚀 Run Locally

```bash
git clone https://github.com/23p61a6680-gif/miai-storyteller.git
cd miai-storyteller

# Install dependencies
pip install -r requirements.txt

# Create a .env file with your API keys
echo GROK_API_KEY=your_groq_key_here   > .env
echo GEMINI_API_KEY=your_gemini_key   >> .env

# Start the app
streamlit run app.py
```

> ⚠️ Never commit your `.env` file — it's already listed in `.gitignore`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit + Custom CSS (Cinzel / Lora fonts, animated gradients) |
| AI Text (Primary) | [Groq](https://console.groq.com/) — Llama 3.3 70B Versatile |
| AI Text (Fallback) | [Google Gemini](https://ai.google.dev/) — 2.5 Flash |
| AI Images | [Pollinations.ai](https://pollinations.ai/) REST API |
| TTS Audio | [gTTS](https://pypi.org/project/gTTS/) — Google Text-to-Speech |
| Env Management | python-dotenv |

---

## 📁 Project Demo

🔗 **[Google Drive — Screen Recording & Assets](https://drive.google.com/drive/folders/11uDepNIVG0h5nenIxFTEtgV0iyPv6M0w?usp=sharing)**

---

*Built for the MirAI School of Technology — Virtual Summer Internship 2026 · Capstone Project.*
