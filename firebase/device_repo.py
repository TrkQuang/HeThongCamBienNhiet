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

def get_device(device_id: str) -> dict:
    db = get_db()
    data = db.reference(f"sensor_data/{device_id}").get()
    if data:
        return {"exists": True, "device_id": device_id}
    return {"exists": False, "device_id": device_id}