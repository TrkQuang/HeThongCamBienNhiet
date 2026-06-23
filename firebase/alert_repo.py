from .client import get_db
import time
import logging

def save_alert(device_id: str, alert_data: dict) -> str:
    db = get_db()
    ref = db.reference(f"alerts/{device_id}")
    # Use Vietnam timezone GMT+7
    from datetime import datetime, timezone, timedelta
    vn_tz = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_tz)
    alert_data.setdefault("timestamp", now_vn.strftime("%Y-%m-%dT%H:%M:%S"))
    alert_data.setdefault("created_at_unix", int(now_vn.timestamp()))
    new_alert_ref = ref.push()
    new_alert_ref.set(alert_data)
    return new_alert_ref.key

def get_recent_alerts(device_id: str, limit: int = 50) -> list:
    """
    Retrieve alerts from Firebase and normalise them to the AlertOut schema.
    Malformed entries are skipped with a warning.
    """
    db = get_db()
    ref = db.reference(f"alerts/{device_id}")
    data = ref.get()
    logging.debug(f"[alert_repo] Raw Firebase data for {device_id}: {data!r}")

    if not data:
        return []

    raw_items = list(data.values())
    normalized = []
    malformed = 0

    for item in raw_items:
        if not isinstance(item, dict):
            malformed += 1
            logging.warning(f"[alert_repo] Skipping non‑dict alert entry: {item!r}")
            continue

        # Build a dict that matches AlertOut fields, filling defaults where needed
        norm = {
            "device_id": device_id,
            "avg_temp": item.get("avg_temp") if item.get("avg_temp") is not None else 0.0,
            "temp": item.get("temp") or item.get("temperature"),
            "percent_increase": item.get("percent_increase") or item.get("percent") or 0.0,
            "threshold": item.get("threshold") or item.get("dangerThreshold") or item.get("warningThreshold") or 0.0,
            "level": item.get("level") or item.get("status") or "UNKNOWN",
            "warning": item.get("warning") or item.get("message") or "",
            "timestamp": item.get("timestamp") or time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "created_at_unix": item.get("created_at_unix") or int(time.time()),
        }
        normalized.append(norm)

    logging.info(f"[alert_repo] {len(normalized)} valid alerts, {malformed} malformed skipped for {device_id}")

    # Sort newest first
    normalized.sort(key=lambda x: x.get("created_at_unix", 0), reverse=True)
    return normalized[:limit]