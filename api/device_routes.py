from typing import Optional
from fastapi import APIRouter, Header
from firebase.device_repo import get_device, get_user_devices, link_device
from firebase.sensor_repo import get_latest_reading
from .schemas import DeviceLink
from .utils import res_err, res_ok

router = APIRouter()

@router.post("/api/devices/link")
def api_link_device(req: DeviceLink, user_id: Optional[str] = Header(None)):
    if not user_id: return res_err("Missing user_id", 401)
    return res_ok(link_device(user_id, req.device_id, req.name), "Linked", 201)

@router.get("/api/devices")
def api_get_devices(user_id: Optional[str] = Header(None)):
    if not user_id: return res_err("Missing user_id", 401)
    return res_ok({"items": get_user_devices(user_id)})

@router.get("/api/devices/{device_id}")
def api_get_device(device_id: str):
    return res_ok(get_device(device_id))

@router.get("/api/sensor/latest/{device_id}")
def api_get_latest_reading(device_id: str):
    doc = get_latest_reading(device_id)
    return doc if doc else res_err("No data", 404)