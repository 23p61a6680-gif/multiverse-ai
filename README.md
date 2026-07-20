# AI Visual Novel Engine — MirAI Capstone

> **A multi-modal, AI-powered "Choose Your Own Adventure" Visual Novel Engine built with Python & Streamlit.**

## 🎥 Project Demo
👉 **[Watch the Demo Video](https://drive.google.com/file/d/1oNNXPmlTB599HnHGZe8Fl4QBnFJSDYjz/view?usp=sharing)**

---

## ✨ Features
| Feature | Description |
|---|---|
| 🧠 **Dual AI Engine** | Uses Groq (Llama 3.3 70B) as the primary AI, with automatic fallback to Gemini 2.5 Flash if rate-limited |
| 📜 **Structured JSON Engine** | Forces the AI to return strict JSON with `story_text`, `image_prompt`, and `options` keys |
| 🎮 **Dynamic Choice UI** | Buttons are generated dynamically from the AI's JSON response — no hardcoded UI |
| 🖼️ **AI Scene Images** | Every scene generates a contextual image via Pollinations.ai (zero token cost) |
| 🔊 **TTS Narration** | Story text is converted to speech using gTTS and autoplays in the browser |
| 📚 **Comic Book History** | Alternating image/text layout lets you re-read your story like a graphic novel |
| ⚡ **Genre Twist** | Changing genre mid-game creates a dramatic AI-written plot transition |
| 🛡️ **Graceful Failures** | All API calls are wrapped in `try/except` — the app never crashes |

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────┐
│  Groq API (Primary — Fast & Free)   │
│  Model: llama-3.3-70b-versatile     │
│  Force JSON: response_format        │
└─────────────┬───────────────────────┘
              │ (on rate-limit / error)
              ▼
┌─────────────────────────────────────┐
│  Gemini 2.5 Flash (Fallback)        │
│  Force JSON: response_mime_type     │
└─────────────┬───────────────────────┘
              │
              ▼
     json.loads(raw_content)
              │
     ┌────────┴─────────┐
     │                  │
     ▼                  ▼
Pollinations.ai      gTTS TTS
(Scene Image)     (MP3 Narration)
     │                  │
     └────────┬─────────┘
              ▼
    Streamlit UI Render
    (Image + Story Card + Choices)
```

### Key Engineering Concepts
- **`@st.cache_resource`** — AI clients are instantiated once and reused
- **Dual session state stores** — `chat_history` (clean, for AI context) and `scene_store` (rich, for comic UI)
- **`try/except` fallback chain** — Groq → Gemini → graceful toast notification
- **Dynamic button loop** — `for opt in options: st.button(opt)` generates the entire choice UI at runtime

---

## 🚀 Run Locally

```bash
git clone https://github.com/23p61a6680-gif/miai-storyteller.git
cd miai-storyteller

# Install dependencies
pip install -r requirements.txt

# Add your API keys to a .env file
echo "GROK_API_KEY=your_groq_key_here" > .env
echo "GEMINI_API_KEY=your_gemini_key_here" >> .env

# Run the app
streamlit run app.py
```

## 🛠️ Tech Stack
- **Frontend:** Streamlit + Custom CSS (Cinzel/Lora fonts, animated gradients)
- **AI Text:** Groq (Llama 3.3 70B) → Gemini 2.5 Flash fallback
- **AI Images:** Pollinations.ai REST API
- **TTS Audio:** gTTS (Google Text-to-Speech)
- **Env Management:** python-dotenv

---
*Built for the MirAI School of Technology Virtual Summer Internship 2026 — Capstone Project.*
