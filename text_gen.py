"""
text_gen.py — Text generation via OpenRouter free models.
"""

from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MAX_TOKENS
from config import TAGLINE_PROMPT, BLOG_INTRO_PROMPT, SOCIAL_POSTS_PROMPT, AUDIO_SCRIPT_PROMPT
from utils import build_context, parse_social_json, friendly_error

# Primary free model — verified working 2026-07
# Fallback chain tried in order if primary returns None or 429
PRIMARY_MODEL = "openai/gpt-oss-20b:free"
FALLBACK_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "openai/gpt-4o-mini",           # paid fallback — uses your OPENROUTER key credits
]


def _call(prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is missing in your .env file.")
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "AI Content Engine",
        },
    )

    models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS
    last_error = None

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
            # content is None or empty — try next model
        except Exception as e:
            last_error = e
            # 404 = model unavailable, 429 = rate limit — try next
            err_str = str(e)
            if "402" in err_str or "404" in err_str or "429" in err_str or "unavailable" in err_str.lower():
                continue
            raise  # unexpected error — surface it immediately

    raise RuntimeError(
        f"All models returned empty content or errors. Last error: {last_error}"
    )


def generate_tagline(product: str, audience: str, tone: str) -> str:
    try:
        return _call(TAGLINE_PROMPT.format(**build_context(product, audience, tone)))
    except Exception as e:
        raise RuntimeError(friendly_error(e, "Tagline")) from e


def generate_blog_intro(product: str, audience: str, tone: str, tagline: str) -> str:
    try:
        return _call(BLOG_INTRO_PROMPT.format(**build_context(product, audience, tone, tagline)))
    except Exception as e:
        raise RuntimeError(friendly_error(e, "Blog")) from e


def generate_social_posts(product: str, audience: str, tone: str, tagline: str) -> dict:
    try:
        raw = _call(SOCIAL_POSTS_PROMPT.format(**build_context(product, audience, tone, tagline)))
        return parse_social_json(raw)
    except Exception as e:
        raise RuntimeError(friendly_error(e, "Social")) from e


def generate_audio_script(product: str, audience: str, tone: str, tagline: str) -> str:
    try:
        return _call(AUDIO_SCRIPT_PROMPT.format(**build_context(product, audience, tone, tagline)))
    except Exception as e:
        raise RuntimeError(friendly_error(e, "Audio script")) from e