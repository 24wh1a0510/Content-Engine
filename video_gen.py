"""
video_gen.py — Promotional video via OpenRouter (Wan 2.6).

API reference:
  Submit  : POST https://openrouter.ai/api/v1/videos
  Poll    : GET  <polling_url>  (from submit response)
  Download: GET  https://openrouter.ai/api/v1/videos/{job_id}/content?index=0
            (auth header required)
  Fallback: unsigned_urls[0] if present (no auth needed)
"""

import time
import httpx
from pathlib import Path
from typing import Callable, Optional, Tuple

from config import OPENROUTER_PAID_KEY, VIDEO_PROMPT_TEMPLATE
from utils import build_context, save_bytes, friendly_error

# ── Correct model slug from openrouter.ai/alibaba/wan-2.6 ────────────────────
VIDEO_MODEL  = "alibaba/wan-2.6"
BASE_URL     = "https://openrouter.ai/api/v1"
SUBMIT_URL   = f"{BASE_URL}/videos"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {OPENROUTER_PAID_KEY}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "http://localhost:8501",
        "X-Title":       "AI Content Engine",
    }


def _submit_job(prompt: str) -> Tuple[str, str]:
    """
    Submit a text-to-video job.
    Returns (job_id, polling_url).
    """
    payload = {
        "model":        VIDEO_MODEL,
        "prompt":       prompt,
        "duration":     5,
        "aspect_ratio": "16:9",
        "resolution":   "720p",
    }
    resp = httpx.post(SUBMIT_URL, headers=_headers(), json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    job_id = data.get("id")
    if not job_id:
        raise RuntimeError(f"No job ID in submit response: {data}")

    # polling_url comes back in the response; fall back to constructed URL
    polling_url = data.get("polling_url") or f"{BASE_URL}/videos/{job_id}"
    return job_id, polling_url


def _poll_job(
    job_id: str,
    polling_url: str,
    max_wait: int = 420,
    interval: int = 20,
    status_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Poll until the job reaches a terminal state.
    Returns the video download URL on success.
    Raises RuntimeError on failure, cancellation, expiry, or timeout.
    """
    waited = 0
    attempt = 0

    while waited < max_wait:
        attempt += 1
        resp = httpx.get(polling_url, headers=_headers(), timeout=15)
        resp.raise_for_status()
        data   = resp.json()
        status = data.get("status", "unknown")

        if status_callback:
            status_callback(f"Video status: {status} (waited {waited}s…)")

        if status == "completed":
            # Prefer the content endpoint (always requires auth header)
            content_url = f"{BASE_URL}/videos/{job_id}/content?index=0"
            # Only use unsigned_urls if they don't point back to OpenRouter API
            unsigned = data.get("unsigned_urls") or []
            if unsigned and not unsigned[0].startswith("https://openrouter.ai/api/"):
                return unsigned[0]          # external CDN — no auth needed
            return content_url              # OpenRouter endpoint — auth in _download

        if status in ("failed", "cancelled", "expired"):
            detail = data.get("error") or data.get("message") or "no detail"
            raise RuntimeError(f"Video job {status}: {detail}")

        time.sleep(interval)
        waited += interval

    raise RuntimeError(
        f"Video generation timed out after {max_wait}s. "
        "The job may still be running — check your OpenRouter dashboard."
    )


def _download(url: str) -> bytes:
    """
    Download video bytes.
    Adds auth header if the URL belongs to the OpenRouter API.
    """
    headers = {}
    if url.startswith("https://openrouter.ai/api/"):
        headers["Authorization"] = f"Bearer {OPENROUTER_PAID_KEY}"

    resp = httpx.get(url, headers=headers, timeout=180, follow_redirects=True)
    resp.raise_for_status()

    # Verify we actually got video bytes, not an error JSON
    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type:
        raise RuntimeError(f"Expected video bytes but got JSON: {resp.text[:200]}")

    return resp.content


def generate_promo_video(
    product: str,
    audience: str,
    tone: str,
    tagline: str,
    status_callback: Optional[Callable[[str], None]] = None,
) -> Path:
    """
    Generate a promotional video via OpenRouter Wan 2.6.
    Returns Path to the saved .mp4 file.
    Raises RuntimeError with a user-friendly message on any failure.
    """
    try:
        if not OPENROUTER_PAID_KEY:
            raise RuntimeError(
                "OPENROUTER_PAID_KEY is missing. "
                "Add it to content_engine/.env as OPENROUTER_PAID_KEY=sk-or-v1-..."
            )

        ctx    = build_context(product, audience, tone, tagline)
        prompt = VIDEO_PROMPT_TEMPLATE.format(**ctx)

        if status_callback:
            status_callback(f"Submitting job to {VIDEO_MODEL}…")

        job_id, polling_url = _submit_job(prompt)

        if status_callback:
            status_callback(f"Job submitted (ID: {job_id[:12]}…). Waiting for Wan 2.6…")

        video_url = _poll_job(
            job_id,
            polling_url,
            status_callback=status_callback,
        )

        if status_callback:
            status_callback("Downloading video…")

        video_bytes = _download(video_url)
        path = save_bytes(video_bytes, stem="promo", ext="mp4")

        if status_callback:
            status_callback(f"Saved to {path.name}")

        return path

    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(friendly_error(e, "Video")) from e
