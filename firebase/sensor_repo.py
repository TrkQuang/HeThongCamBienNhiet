from .client import get_db
import datetime

def save_reading(device_id: str, reading_data: dict) -> str:
    db = get_db()
    ref = db.reference(f"sensor_data/{device_id}")
    new_reading_ref = ref.push()
    new_reading_ref.set(reading_data)
    return new_reading_ref.key

def get_recent_readings(device_id: str, limit: int = 50) -> list:
    db = get_db()
    ref = db.reference(f"sensor_data/{device_id}")
    data = ref.get()
    if not data:
        return []
        
    items = list(data.values())
    # Sort by timestamp, newest first. ESP may write either "timestamp" or legacy "ts".
    items.sort(key=lambda x: x.get("timestamp") or x.get("ts", ""), reverse=True)
    return items[:limit]

def get_latest_reading(device_id: str) -> dict:
    db = get_db()
    ref = db.reference(f"sensor_data/{device_id}")
    data = ref.get()
    if not data:
        return None
        
    items = list(data.values())
    items.sort(key=lambda x: x.get("timestamp") or x.get("ts", ""), reverse=True)
    latest_val = items[0]
    
    # Fix typo 'wanning' in database
    warning = latest_val.get("warning") or latest_val.get("wanning", "")
    
    return {
        "device_id": device_id,
        "temp": float(latest_val.get("temp", 0)),
        "humidity": float(latest_val.get("humidity", 0)),
        "timestamp": latest_val.get("timestamp") or latest_val.get("ts", ""),
        "warning": warning
    }
