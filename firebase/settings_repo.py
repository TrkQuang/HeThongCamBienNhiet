from .client import get_db

def get_settings(device_id: str) -> dict:
    db = get_db()
    return db.reference(f"settings/{device_id}").get()

def update_settings(device_id: str, settings: dict) -> dict:
    db = get_db()
    ref = db.reference(f"settings/{device_id}")
    ref.update(settings)
    return ref.get()
