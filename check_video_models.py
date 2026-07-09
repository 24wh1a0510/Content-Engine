"""
Check available video models on OpenRouter.
Run: python check_video_models.py
"""
import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
PAID_KEY = os.getenv("OPENROUTER_PAID_KEY", "")

resp = httpx.get(
    "https://openrouter.ai/api/v1/videos/models",
    headers={"Authorization": f"Bearer {PAID_KEY}"},
    timeout=15,
)
print(f"Status: {resp.status_code}")
data = resp.json()
models = data.get("data", [])
print(f"\nAvailable video models ({len(models)}):\n")
for m in models:
    print(f"  ID       : {m.get('id')}")
    print(f"  Durations: {m.get('supported_durations')}")
    print(f"  Aspects  : {m.get('supported_aspect_ratios')}")
    print()