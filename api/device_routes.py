from fastapi import APIRouter, status, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from firebase.device_repo import link_device, get_user_devices, get_device
from firebase.sensor_repo import get_latest_reading
from .schemas import DeviceLink, ApiResponse, ErrorResponse

router = APIRouter()

@router.post("/api/devices/link")
def api_link_device(req: DeviceLink, user_id: Optional[str] = Header(None)):
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Missing user_id header"})
        
    device_data = link_device(user_id, req.device_id, req.name)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=ApiResponse(status="success", message="Đã liên kết thiết bị", data=device_data).model_dump()
    )

@router.get("/api/devices")
def api_get_devices(user_id: Optional[str] = Header(None)):
    if not user_id:
        return JSONResponse(status_code=401, content={"trang_thai": "error", "thong_diep": "Missing user_id header"})
        
    devices = get_user_devices(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ApiResponse(status="success", message="OK", data={"items": devices}).model_dump()
    )

@router.get("/api/devices/{device_id}")
def api_get_device(device_id: str):
    dev = get_device(device_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ApiResponse(status="success", message="OK", data=dev).model_dump()
    )

@router.get("/api/sensor/latest/{device_id}")
def api_get_latest_reading(device_id: str):
    reading = get_latest_reading(device_id)
    if not reading:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(status="error", message="Không có dữ liệu", errors=[]).model_dump()
        )
    return reading