from fastapi import APIRouter
from firebase.device_repo import get_device, get_user_devices, link_device
from firebase.sensor_repo import get_latest_reading
from .schemas import DeviceLink
from .utils import res_err, res_ok

router = APIRouter()

@router.post("/api/devices/link")
def api_link_device(req: DeviceLink):
    return res_ok(link_device("default_user", req.device_id, req.name), "Linked", 201)

@router.get("/api/devices")
def api_get_devices():
    return res_ok({"items": get_user_devices("default_user")})

@router.get("/api/devices/{device_id}")
def api_get_device(device_id: str):
    return res_ok(get_device(device_id))

@router.get("/api/sensor/latest/{device_id}")
def api_get_latest_reading(device_id: str):
    doc = get_latest_reading(device_id)
    return doc if doc else res_err("No data", 404)