from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict


_SETTINGS_PATH = Path("config/ui_settings.json")


@dataclass
class AppSettings:
    api_base_url: str = "http://127.0.0.1:5000"
    sensor_id: str = ""
    warning_threshold: float = 35.0
    danger_threshold: float = 40.0
    refresh_ms: int = 3000
    sound_alert: bool = True
    email_alert: bool = False


def _load_yaml_settings() -> Dict[str, Any]:
    path = Path("config/settings.yaml")
    if not path.is_file():
        return {}

    try:
        import yaml

        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except Exception:
        return {}


def _guess_api_base_url() -> str:
    env_url = os.getenv("API_BASE_URL")
    if env_url:
        return env_url.strip().rstrip("/")

    settings = _load_yaml_settings()
    api_settings = settings.get("api", {})
    host = api_settings.get("host", "127.0.0.1")
    port = api_settings.get("port", 5000)
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    return f"http://{host}:{port}"


def load_settings() -> AppSettings:
    settings = AppSettings(api_base_url=_guess_api_base_url())

    if _SETTINGS_PATH.is_file():
        try:
            data = json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

    return settings


def save_settings(settings: AppSettings) -> None:
    _SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(settings)
    _SETTINGS_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
