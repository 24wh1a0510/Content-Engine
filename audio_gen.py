"""
audio_gen.py — Voiceover audio via OpenAI TTS (tts-1).

Uses OPENAI_API_KEY directly since OpenRouter does not expose a standard
/audio/speech endpoint for tts-1.
Falls back to script-only (no audio file) if no key or credits.
"""

from pathlib import Path
from typing import Optional, Tuple

from config import OPENAI_API_KEY
from utils import save_bytes, friendly_error
from text_gen import generate_audio_script

AUDIO_MODEL = "tts-1"
AUDIO_VOICE = "nova"


def generate_voiceover(
    product: str,
    audience: str,
    tone: str,
    tagline: str,
) -> Tuple[Optional[Path], str]:
    """
    Generate a voiceover MP3 via OpenAI TTS.
    Always returns (path_or_None, script_text).
    Raises RuntimeError only if script generation itself fails.
    """
    # Step 1 — generate the script (always, even without audio key)
    script = generate_audio_script(product, audience, tone, tagline)

    # Step 2 — generate audio if we have an OpenAI key
    if not OPENAI_API_KEY:
        return None, script

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.audio.speech.create(
            model=AUDIO_MODEL,
            voice=AUDIO_VOICE,
            input=script,
            response_format="mp3",
        )
        audio_bytes = response.content
        path = save_bytes(audio_bytes, stem="voiceover", ext="mp3")
        return path, script

    except Exception as e:
        # Audio is non-critical — log and continue without it
        print(f"[Audio] TTS failed (non-fatal): {friendly_error(e, 'Audio')}")
        return None, script
