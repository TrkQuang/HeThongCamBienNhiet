from fastapi import APIRouter
from firebase.settings_repo import get_settings, update_settings
from .schemas import DeviceSettings
from .utils import res_err, res_ok

router = APIRouter()

@router.get("/api/settings/{device_id}")
def get_device_settings(device_id: str):
    cai_dat = get_settings(device_id)
    if cai_dat is None: return res_err("Settings not found", 404)
    return res_ok(cai_dat)

@router.put("/api/settings/{device_id}")
def update_device_settings(device_id: str, settings: DeviceSettings):
    cap_nhat = settings.model_dump(exclude_unset=True)
    if not cap_nhat: return res_err("No fields provided for update")
    return res_ok(update_settings(device_id, cap_nhat), "Settings updated")