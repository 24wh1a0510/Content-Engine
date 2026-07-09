# ⚡ AI Content Engine

> **One Brief In → Five Creative Assets Out**

A production-ready Streamlit application that turns a short product brief into a full campaign kit — tagline, blog intro, social posts, hero image, and a promotional video concept — in under 60 seconds.

---

## ✨ Features

| Asset | Provider |
|---|---|
| 💡 Campaign Tagline | Claude (Anthropic) |
| 📰 Blog Introduction (~200 words) | Claude (Anthropic) |
| 📲 Social Posts (Twitter · Instagram · LinkedIn) | Claude (Anthropic) |
| 🎨 Hero Image | DALL-E 3 (OpenAI) or Stability AI |
| 🎬 Promotional Video Concept | Claude (Anthropic) |

---

## 🚀 Quick Start

### 1. Clone / download the project

```bash
git clone <your-repo-url>
cd content_engine
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

```bash
cp .env.example .env
# Open .env and paste your Anthropic and OpenAI API keys
```

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🗂️ Project Structure

```
content_engine/
│
├── app.py          ← Streamlit UI — layout, state, progress
├── text_gen.py     ← All Claude text generation (tagline, blog, social, video concept)
├── image_gen.py    ← Hero image generation (DALL-E 3 / Stability AI / placeholder)
├── video_gen.py    ← Video concept packager (extend with Runway / Kling / Pika)
├── config.py       ← API keys, model names, and all prompt templates
├── utils.py        ← Shared helpers: context builder, JSON parser, image saver
│
├── assets/         ← Auto-created; generated images saved here
│
├── .env.example    ← Environment variable template
├── requirements.txt
└── README.md
```

---

## 🔧 Customisation

### Swap the text model
Edit `TEXT_MODEL` in `config.py`. Any Anthropic model string works.

### Change prompts
All prompts live in `config.py` as multi-line string constants. Edit them freely — the rest of the code is prompt-agnostic.

### Use Stability AI instead of DALL-E
Set `USE_STABILITY=true` in your `.env` and supply a `STABILITY_API_KEY`.

### Add real video rendering
In `video_gen.py`, replace the `None` return for `video_path` with a call to a video API (Runway ML, Kling, Pika Labs, etc.) and return the local path to the rendered file. `app.py` will automatically render it via `st.video()`.

### Add a new tone
In `config.py`, add an entry to `TONE_DESCRIPTORS` and add the label to the `selectbox` in `app.py`.

---

## 🔑 API Keys

| Key | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) |
| `STABILITY_API_KEY` | [platform.stability.ai](https://platform.stability.ai) |

---

## 🛡️ Notes

- The app runs in **demo mode** (no image key needed) — image cards will show a placeholder and all text assets still generate normally.
- Generated images are saved to `assets/` with timestamps so nothing is overwritten.
- No data is stored server-side beyond the local `assets/` folder.

---

## 📄 License

MIT — do whatever you like with it.
