from .client import get_db
import firebase_admin

def save_alert(device_id: str, alert_data: dict) -> str:
    db = get_db()
    ref = db.reference(f"alerts/{device_id}")
    new_alert_ref = ref.push()
    alert_data["created_at_unix"] = alert_data.get("created_at_unix", int(firebase_admin.db.SERVER_TIMESTAMP))
    new_alert_ref.set(alert_data)
    return new_alert_ref.key

def get_recent_alerts(device_id: str, limit: int = 50) -> list:
    db = get_db()
    ref = db.reference(f"alerts/{device_id}")
    data = ref.get()
    if not data:
        return []
        
    items = list(data.values())
    items.sort(key=lambda x: x.get("created_at_unix", 0), reverse=True)
    return items[:limit]
