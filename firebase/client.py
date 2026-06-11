import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, db

_DEFAULT_CREDENTIALS_PATH = "iot/key_firebase_HeThongNhiet.json"
_DEFAULT_DATABASE_URL = "https://hethongcambiennhiet-default-rtdb.asia-southeast1.firebasedatabase.app/"

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

def get_firebase_app():
    try:
        return firebase_admin.get_app()
    except ValueError:
        credentials_path, database_url = _firebase_config()
        if not credentials_path or not database_url:
            raise RuntimeError("Firebase settings are missing. Set FIREBASE_CREDENTIALS and FIREBASE_DATABASE_URL.")
        cred = credentials.Certificate(credentials_path)
        return firebase_admin.initialize_app(cred, {"databaseURL": database_url})

def get_db():
    get_firebase_app()
    return db
