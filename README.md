# 🚀 Content Engine

**Content Engine** is a multimodal AI-powered content generation application built with **Streamlit**. It transforms a simple product brief into a complete marketing campaign by generating high-quality text, images, and videos using multiple AI models.

## ✨ Features

* 📝 AI-generated Campaign Tagline
* 📖 200-word Blog Introduction
* 📱 Social Media Posts

  * Twitter/X
  * Instagram
  * LinkedIn
* 🎨 AI-generated Hero Image
* 🎬 AI-generated Promotional Video
* ⚡ One-click generation from a single product brief

---

## 🏗️ Tech Stack

* **Frontend:** Streamlit
* **Language:** Python 3.11+
* **Framework:** Streamlit
* **LLM Provider:** OpenRouter API
* **Image Generation:** OpenAI GPT Image API
* **Video Generation:** Alibaba Wan 2.6 Model
* **Environment Management:** python-dotenv

---

## 📂 Project Structure

```text
content_engine/
│
├── app.py
├── text_gen.py
├── image_gen.py
├── video_gen.py
├── config.py
├── utils.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Prerequisites

* Python 3.11 or later
* OpenRouter API Key
* OpenAI API Key

---

## 🔑 Environment Variables

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENAI_API_KEY=your_openai_api_key
```

---

## 📦 Installation

Clone the repository.

```bash
git clone <your-repository-url>
cd content_engine
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the virtual environment.

### Windows

```bash
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

Install the required dependencies.

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

---

## 🚀 How It Works

1. Enter the **Product Name**.
2. Enter the **Target Audience**.
3. Select the **Brand Tone**.
4. Click **Generate Campaign**.
5. The application generates:

   * Campaign Tagline
   * Blog Introduction
   * Social Media Posts
   * Hero Image
   * Promotional Video

---

## 🤖 AI Models Used

| Task             | Model / Service      |
| ---------------- | -------------------- |
| Text Generation  | OpenRouter LLM       |
| Image Generation | OpenAI GPT Image API |
| Video Generation | Alibaba Wan 2.6      |

---

## 📸 Outputs

The application generates a complete marketing campaign consisting of:

* Campaign Tagline
* Blog Introduction
* Social Media Posts
* Hero Image
* Promotional Video
