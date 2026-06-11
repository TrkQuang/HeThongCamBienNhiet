from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from firebase.settings_repo import get_settings, update_settings
from .schemas import DeviceSettings, ApiResponse, ErrorResponse

router = APIRouter()

@router.get("/api/settings/{device_id}")
def api_get_settings(device_id: str):
    data = get_settings(device_id)
    if not data:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(status="error", message="Không tìm thấy cấu hình", errors=[]).model_dump()
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ApiResponse(status="success", message="OK", data=data).model_dump()
    )

@router.put("/api/settings/{device_id}")
def api_put_settings(device_id: str, settings: DeviceSettings):
    updates = settings.model_dump(exclude_unset=True)
    if not updates:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(status="error", message="Không có dữ liệu cập nhật", errors=[]).model_dump()
        )
    
    updated_data = update_settings(device_id, updates)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ApiResponse(status="success", message="Đã cập nhật cấu hình", data=updated_data).model_dump()
    )
