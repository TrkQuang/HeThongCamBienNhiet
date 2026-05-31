from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, db as fb_db


_DEFAULT_CREDENTIALS_PATH = "iot/key_firebase_HeThongNhiet.json"
_DEFAULT_DATABASE_URL = "https://hethongcambiennhiet-default-rtdb.asia-southeast1.firebasedatabase.app/"

_INTERNAL_READING_KEYS = {"server_ts_unix"}
_INTERNAL_ALERT_KEYS = {"created_at_unix"}


def _load_settings() -> dict:
    path = Path("config/settings.yaml")
    if not path.is_file():
        return {}

    try:
        import yaml

        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except Exception:
        return {}


def _firebase_config() -> tuple[str, str]:
    settings = _load_settings()
    fb_settings = settings.get("firebase", {})

    credentials_path = os.getenv("FIREBASE_CREDENTIALS") or fb_settings.get("credentials_path") or _DEFAULT_CREDENTIALS_PATH
    database_url = os.getenv("FIREBASE_DATABASE_URL") or fb_settings.get("database_url") or _DEFAULT_DATABASE_URL
    return str(credentials_path), str(database_url)


def _ensure_app() -> None:
    try:
        firebase_admin.get_app()
        return
    except ValueError:
        pass

    credentials_path, database_url = _firebase_config()
    if not credentials_path or not database_url:
        raise RuntimeError("Firebase settings are missing. Set FIREBASE_CREDENTIALS and FIREBASE_DATABASE_URL.")

    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred, {"databaseURL": database_url})


def _parse_datetime(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def _with_server_ts(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(payload)
    server_dt = _parse_datetime(data.get("server_ts"))
    if server_dt is None:
        server_dt = datetime.now(timezone.utc)
        data["server_ts"] = server_dt.isoformat()
    data["server_ts_unix"] = int(server_dt.timestamp())
    return data


def _with_created_ts(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(payload)
    created_dt = _parse_datetime(data.get("created_at"))
    if created_dt is None:
        created_dt = datetime.now(timezone.utc)
        data["created_at"] = created_dt.isoformat()
    data["created_at_unix"] = int(created_dt.timestamp())
    return data


def _strip_internal(items: List[Dict[str, Any]], keys: set[str]) -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []
    for item in items:
        cleaned.append({k: v for k, v in item.items() if k not in keys})
    return cleaned


def _query_recent(path: str, order_key: str, limit: int) -> List[Dict[str, Any]]:
    _ensure_app()
    ref = fb_db.reference(path)
    snapshot = ref.order_by_child(order_key).limit_to_last(limit).get()
    items = list(snapshot.values()) if snapshot else []
    items.sort(key=lambda x: x.get(order_key, 0), reverse=True)
    return items


def save_reading(payload: Dict[str, Any]) -> str:
    _ensure_app()
    data = _with_server_ts(payload)
    sensor_id = data.get("sensor_id")

    root = fb_db.reference("/")
    new_key = fb_db.reference("readings").push().key
    if not new_key:
        raise RuntimeError("Failed to create Firebase key for reading")

    updates = {f"readings/{new_key}": data}
    if sensor_id:
        updates[f"readings_by_sensor/{sensor_id}/{new_key}"] = data
    root.update(updates)
    return new_key


def save_alert(payload: Dict[str, Any]) -> str:
    _ensure_app()
    data = _with_created_ts(payload)
    sensor_id = data.get("sensor_id")

    root = fb_db.reference("/")
    new_key = fb_db.reference("alerts").push().key
    if not new_key:
        raise RuntimeError("Failed to create Firebase key for alert")

    updates = {f"alerts/{new_key}": data}
    if sensor_id:
        updates[f"alerts_by_sensor/{sensor_id}/{new_key}"] = data
    root.update(updates)
    return new_key


def get_recent_readings(sensor_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    path = f"readings_by_sensor/{sensor_id}" if sensor_id else "readings"
    items = _query_recent(path, "server_ts_unix", limit)
    return _strip_internal(items, _INTERNAL_READING_KEYS)


def get_recent_alerts(sensor_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    path = f"alerts_by_sensor/{sensor_id}" if sensor_id else "alerts"
    items = _query_recent(path, "created_at_unix", limit)
    return _strip_internal(items, _INTERNAL_ALERT_KEYS)
