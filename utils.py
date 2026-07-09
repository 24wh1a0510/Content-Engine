"""
utils.py — Shared helper functions.
"""

import json
import re
import base64
from pathlib import Path
from datetime import datetime


def build_context(product: str, audience: str, tone: str, tagline: str = "") -> dict:
    from config import TONE_DESCRIPTORS
    return {
        "product":   product,
        "audience":  audience,
        "tone":      tone,
        "tone_desc": TONE_DESCRIPTORS.get(tone, tone),
        "tagline":   tagline,
    }


def parse_social_json(raw: str) -> dict:
    """
    Robustly extract JSON from model response.
    Handles markdown fences, extra prose, and nested quotes.
    """
    # Strip markdown fences
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    # Find the outermost { ... } block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        data = json.loads(cleaned)
        return {
            "twitter":   data.get("twitter", ""),
            "instagram": data.get("instagram", ""),
            "linkedin":  data.get("linkedin", ""),
        }
    except json.JSONDecodeError:
        # Last resort: extract values with regex
        def extract(key):
            m = re.search(rf'"{key}"\s*:\s*"(.*?)"(?=\s*[,}}])', cleaned, re.DOTALL)
            return m.group(1).replace("\\n", "\n") if m else ""

        return {
            "twitter":   extract("twitter"),
            "instagram": extract("instagram"),
            "linkedin":  extract("linkedin"),
        }


def save_bytes(data: bytes, stem: str, ext: str) -> Path:
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = assets_dir / f"{stem}_{timestamp}.{ext}"
    path.write_bytes(data)
    return path


def friendly_error(exc: Exception, context: str = "") -> str:
    msg = str(exc)
    prefix = f"[{context}] " if context else ""
    if "401" in msg or "authentication" in msg.lower() or "api key" in msg.lower():
        return f"{prefix}API key missing or invalid. Check your .env file."
    if "429" in msg or "rate limit" in msg.lower():
        return f"{prefix}Rate limit hit — wait a moment and try again."
    if "timeout" in msg.lower():
        return f"{prefix}Request timed out. Check your internet connection."
    return f"{prefix}Unexpected error: {msg}"