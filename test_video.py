"""
Test video generation directly.
Run: python test_video.py
"""
import os
import time
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
PAID_KEY = os.getenv("OPENROUTER_PAID_KEY", "")

HEADERS = {
    "Authorization": f"Bearer {PAID_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:8501",
    "X-Title": "AI Content Engine",
}

print("Submitting video job...")
resp = httpx.post(
    "https://openrouter.ai/api/v1/videos",
    headers=HEADERS,
    json={
        "model": "alibaba/wan-2.6",
        "prompt": "A cinematic promotional video for a water bottle brand. Clean, modern, professional.",
        "duration": 5,
        "aspect_ratio": "16:9",
    },
    timeout=30,
)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

if resp.status_code == 200:
    data = resp.json()
    job_id = data.get("id")
    poll_url = data.get("polling_url", f"https://openrouter.ai/api/v1/videos/{job_id}")
    print(f"\nJob ID: {job_id}")
    print(f"Polling URL: {poll_url}")
    print("\nPolling every 15s (max 3 attempts)...")
    for i in range(3):
        time.sleep(15)
        r = httpx.get(poll_url, headers=HEADERS, timeout=15)
        d = r.json()
        print(f"  Attempt {i+1}: status={d.get('status')} data={d}")
        if d.get("status") in ("completed", "failed"):
            break