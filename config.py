"""
config.py — Central configuration and prompt templates.

Provider split:
  Text   → OpenRouter FREE key (llama-3.1-8b free)
  Image  → OpenRouter FREE key (flux-schnell free)
  Audio  → OpenAI key (TTS) — optional, falls back to script-only
  Video  → OpenRouter PAID key (Wan 2.6)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ── API Keys ───────────────────────────────────────────────────────────────────
OPENAI_API_KEY         = os.getenv("OPENAI_API_KEY", "")
OPENROUTER_API_KEY     = os.getenv("OPENROUTER_API_KEY", "")      # free key
OPENROUTER_PAID_KEY    = os.getenv("OPENROUTER_PAID_KEY", "")     # paid key (video only)

# ── Endpoints & Models ─────────────────────────────────────────────────────────
OPENROUTER_BASE_URL    = "https://openrouter.ai/api/v1"

TEXT_MODEL   = "meta-llama/llama-3.1-8b-instruct:free"
IMAGE_MODEL  = "black-forest-labs/flux-1-schnell:free"
AUDIO_MODEL  = "tts-1"
AUDIO_VOICE  = "nova"
VIDEO_MODEL  = "alibaba/wan-2.6"        # correct slug — openrouter.ai/alibaba/wan-2.6

MAX_TOKENS = 400   # kept low so free-tier credits are not exhausted in one call

# ── Tone descriptors ───────────────────────────────────────────────────────────
TONE_DESCRIPTORS = {
    "Playful": "fun, witty, youthful, uses light humour and casual language",
    "Premium": "sophisticated, polished, luxurious, aspirational, minimal jargon",
    "Eco":     "warm, earthy, conscious, purpose-driven, community-oriented",
    "Modern":  "clean, bold, forward-thinking, tech-savvy, direct",
}

# ── Prompt templates ───────────────────────────────────────────────────────────

TAGLINE_PROMPT = """
You are a world-class copywriter. Write ONE compelling campaign tagline for:

Product / Brand : {product}
Target Audience : {audience}
Brand Tone      : {tone_desc}

Rules:
- Maximum 10 words
- No quotation marks
- Return ONLY the tagline, nothing else
""".strip()

BLOG_INTRO_PROMPT = """
You are a content strategist. Write a 120-word blog introduction for:

Product / Brand : {product}
Target Audience : {audience}
Brand Tone      : {tone_desc}
Campaign Tagline: {tagline}

Rules:
- Exactly ~120 words
- Hook the reader in the first sentence
- End with a soft call-to-action
- No headers or bullet points, flowing prose only
""".strip()

SOCIAL_POSTS_PROMPT = """
You are a social media expert. Output ONLY a JSON object, nothing else.
No markdown, no explanation, no backticks. Just the raw JSON.

Product: {product}
Audience: {audience}
Tone: {tone_desc}
Tagline: {tagline}

Required format (keep each value short):
{{"twitter":"tweet under 200 chars with 1 hashtag","instagram":"caption 2 sentences with 3 hashtags","linkedin":"professional post 2 sentences no hashtags"}}
""".strip()

AUDIO_SCRIPT_PROMPT = """
You are a voiceover scriptwriter. Write a 20-second radio ad script for:

Product / Brand : {product}
Target Audience : {audience}
Brand Tone      : {tone_desc}
Campaign Tagline: {tagline}

Rules:
- Max 50 words
- Start with a hook, end with the tagline
- Natural spoken English only
- Return ONLY the script text
""".strip()

IMAGE_PROMPT_TEMPLATE = """
A high-quality hero marketing image for '{product}' targeting '{audience}'.
Style: {tone_desc}.
Campaign tagline: '{tagline}'.
Clean, professional, photorealistic, suitable for a brand campaign.
Wide aspect ratio, no text overlays.
""".strip()

VIDEO_PROMPT_TEMPLATE = """
A cinematic 5-second promotional video for '{product}' targeting '{audience}'.
Tone: {tone_desc}.
Campaign tagline: '{tagline}'.
Visual style: clean, modern, professional brand advertisement.
Smooth camera movement, lifestyle shots, product in use.
""".strip()