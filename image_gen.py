"""
image_gen.py — Hero image generation.
Uses OpenAI DALL-E 3 if OPENAI_API_KEY has credits.
Falls back to a styled SVG placeholder if no credits available.
"""

import base64
import hashlib
from pathlib import Path

from config import OPENAI_API_KEY, IMAGE_PROMPT_TEMPLATE
from utils import build_context, save_bytes, friendly_error

TONE_PALETTES = {
    "Playful": {"bg": "#FFF7ED", "accent": "#F97316", "text": "#9A3412", "shape": "#FDBA74"},
    "Premium": {"bg": "#0F172A", "accent": "#C4A35A", "text": "#E2D9C8", "shape": "#1E293B"},
    "Eco":     {"bg": "#F0FDF4", "accent": "#16A34A", "text": "#14532D", "shape": "#BBF7D0"},
    "Modern":  {"bg": "#EFF6FF", "accent": "#3B82F6", "text": "#1E3A8A", "shape": "#BFDBFE"},
}


def _svg_placeholder(product: str, tagline: str, tone: str) -> bytes:
    """Generate a branded SVG hero image as fallback."""
    p = TONE_PALETTES.get(tone, TONE_PALETTES["Modern"])
    bg, accent, txt, shape = p["bg"], p["accent"], p["text"], p["shape"]

    seed = int(hashlib.md5(product.encode()).hexdigest()[:8], 16)
    circles = ""
    for i in range(7):
        cx = 60 + (seed * (i + 1) * 137) % 500
        cy = 30 + (seed * (i + 1) * 97) % 240
        r  = 15 + (seed * (i + 3) * 53) % 70
        circles += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{shape}" opacity="0.2"/>\n'

    dp = product[:30] + ("…" if len(product) > 30 else "")
    dt = tagline[:55] + ("…" if len(tagline) > 55 else "")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 320" width="640" height="320">
  <rect width="640" height="320" fill="{bg}"/>
  {circles}
  <rect x="0" y="0" width="6" height="320" fill="{accent}"/>
  <rect x="0" y="280" width="640" height="40" fill="{accent}" opacity="0.08"/>
  <text x="36" y="100" font-family="Georgia,serif" font-size="11" fill="{accent}" font-weight="bold" letter-spacing="3">CAMPAIGN HERO IMAGE</text>
  <text x="36" y="165" font-family="Georgia,serif" font-size="36" fill="{txt}" font-weight="bold">{dp}</text>
  <text x="36" y="205" font-family="Arial,sans-serif" font-size="17" fill="{txt}" opacity="0.7" font-style="italic">{dt}</text>
  <text x="36" y="300" font-family="Arial,sans-serif" font-size="11" fill="{accent}" opacity="0.5">Add OPENAI_API_KEY with credits for a real DALL-E 3 image</text>
</svg>"""
    return svg.encode("utf-8")


def generate_hero_image(product: str, audience: str, tone: str, tagline: str) -> Path:
    """
    Generate hero image via DALL-E 3 if OpenAI key has credits,
    otherwise generate a styled SVG placeholder.
    """
    ctx = build_context(product, audience, tone, tagline)

    # Try DALL-E 3 first
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            prompt = IMAGE_PROMPT_TEMPLATE.format(**ctx)
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="standard",
                response_format="b64_json",
                n=1,
            )
            image_bytes = base64.b64decode(response.data[0].b64_json)
            return save_bytes(image_bytes, stem="hero", ext="png")
        except Exception:
            pass  # Fall through to SVG placeholder

    # SVG placeholder fallback — always works, no key needed
    svg_bytes = _svg_placeholder(product, tagline, tone)
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    from datetime import datetime
    path = assets_dir / f"hero_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"
    path.write_bytes(svg_bytes)
    return path