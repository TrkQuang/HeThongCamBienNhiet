from .client import get_db
import datetime

def link_device(user_id: str, device_id: str, name: str) -> dict:
    """Links a device to a user."""
    db = get_db()
    
    device_ref = db.reference(f"devices/{device_id}")
    
    device_data = {
        "device_id": device_id,
        "user_id": user_id,
        "name": name,
        "linked_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    device_ref.set(device_data)
    
    db.reference(f"users/{user_id}/devices/{device_id}").set(True)
    
    settings_ref = db.reference(f"settings/{device_id}")
    if not settings_ref.get():
        settings_ref.set({
            "temperatureThreshold": 40.0,
            "dangerThreshold": 45.0,
            "humidityThreshold": 80.0,
            "samplingInterval": 10,
            "notificationEnabled": True
        })
        
    return device_data

def get_user_devices(user_id: str) -> list:
    db = get_db()
    user_devices_ref = db.reference(f"users/{user_id}/devices")
    device_ids = user_devices_ref.get()
    if not device_ids:
        return []
    
    devices = []
    for device_id in device_ids.keys():
        dev = db.reference(f"devices/{device_id}").get()
        if dev:
            devices.append(dev)
    return devices

def delete_device(user_id: str, device_id: str) -> None:
    """Delete a device completely from all Firebase paths."""
    db = get_db()
    paths = [
        f"alerts/{device_id}",
        f"measure_requests/{device_id}",
        f"sensor_data/{device_id}",
        f"settings/{device_id}",
        f"devices/{device_id}",
        f"users/{user_id}/devices/{device_id}",
    ]
    for p in paths:
        try:
            db.reference(p).delete()
        except Exception as e:
            print(f"[DELETE] error at {p}: {e}")

def get_device(device_id: str) -> dict:
    """Check if device exists by looking at the devices/ path (not sensor_data/).

    The old code checked sensor_data/{device_id}, which fails for newly-linked
    devices that haven't sent data yet.  Check devices/{device_id} instead.
    """
    db = get_db()
    # Also check the devices collection — a device linked via link_device()
    # writes to devices/{device_id} even before sensor data arrives.
    data = db.reference(f"devices/{device_id}").get()
    if data and data.get("device_id") == device_id:
        return {"exists": True, "device_id": device_id}
    # Fallback to sensor_data for backwards compat
    data = db.reference(f"sensor_data/{device_id}").get()
    if data:
        return {"exists": True, "device_id": device_id}
    return {"exists": False, "device_id": device_id}