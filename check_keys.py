import os, httpx
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("OPENROUTER_PAID_KEY")
resp = httpx.get(
    "https://openrouter.ai/api/v1/credits",
    headers={"Authorization": f"Bearer {key}"},
    timeout=10,
)
print(resp.status_code, resp.json())