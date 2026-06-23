import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Optional


load_dotenv()

def _get_gemini():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def goi_ai(prompt: str) -> Optional[str]:
    try:
        model = _get_gemini()

        resp = model.generate_content(
    "Bạn là chuyên gia IoT về hệ thống giám sát nhiệt độ và độ ẩm công nghiệp. "
    "Trả lời ngắn gọn bằng tiếng Việt, mỗi gợi ý một dòng, tập trung hành động khắc phục.\n\n"
    f"Dữ liệu: {prompt}")

        if not resp or not resp.text:
            print("[AI] Empty response")
            return None

        return resp.text.strip()

    except Exception as e:
        print(f"[AI GEMINI ERROR] {e}")
        return None
