from __future__ import annotations
import json, os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

_DUONG_DAN = Path("devices.json")

@dataclass
class AppSettings:
    api_base_url: str = "http://127.0.0.1:5000"
    device_id: str = ""
    devices: List[Dict[str, str]] = field(default_factory=list)
    warning_threshold: float = 35.0
    danger_threshold: float = 40.0
    humidity_threshold: float = 80.0
    refresh_ms: int = 3000
    sound_alert: bool = True
    email_alert: bool = False

def _doan_api_url() -> str:
    # Ưu tiên biến môi trường, fallback settings.yaml
    env_url = os.getenv("API_BASE_URL")
    if env_url: return env_url.strip().rstrip("/")
    try:
        import yaml
        cau_hinh = yaml.safe_load(Path("config/settings.yaml").read_text(encoding="utf-8")) or {}
        api = cau_hinh.get("api", {})
        host = api.get("host", "127.0.0.1")
        port = api.get("port", 5000)
        if host in {"0.0.0.0", "::"}: host = "127.0.0.1"
        return f"http://{host}:{port}"
    except: return "http://127.0.0.1:5000"

def load_settings() -> AppSettings:
    cai_dat = AppSettings(api_base_url=_doan_api_url())
    if _DUONG_DAN.is_file():
        try:
            du_lieu = json.loads(_DUONG_DAN.read_text(encoding="utf-8"))
            for k, v in du_lieu.items():
                if hasattr(cai_dat, k): setattr(cai_dat, k, v)
        except: pass
    return cai_dat

def save_settings(cai_dat: AppSettings):
    _DUONG_DAN.parent.mkdir(parents=True, exist_ok=True)
    _DUONG_DAN.write_text(json.dumps(asdict(cai_dat), ensure_ascii=False, indent=2), encoding="utf-8")