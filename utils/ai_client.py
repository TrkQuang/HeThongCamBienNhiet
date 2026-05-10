import os
from typing import Optional

import requests


def goi_ai(prompt: str) -> Optional[str]:
    """Gọi dịch vụ AI nếu đã cấu hình, nếu không thì trả về None."""
    api_url = os.getenv("AI_API_URL", "").strip()
    api_key = os.getenv("AI_API_KEY", "").strip()
    timeout = float(os.getenv("AI_TIMEOUT", "10"))

    if not api_url:
        return None

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "prompt": prompt,
        "max_tokens": 120,
        "temperature": 0.3,
    }

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("text") or data.get("result")
    except Exception:
        return None
