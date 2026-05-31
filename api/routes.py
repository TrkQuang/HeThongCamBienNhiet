from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from .schemas import AlertOut, ApiResponse, DuLieuNhietRa, DuLieuNhietVao, ErrorResponse
from core.aggregator import tinh_trung_binh, xu_ly_canh_bao
from core.thresholds import NGUONG_CANH_BAO
from utils.firebase_store import get_recent_alerts, get_recent_readings, save_alert, save_reading
from utils.logger import logger
from utils.validators import kiem_tra_du_lieu

router = APIRouter()


@router.post("/api/du-lieu-nhiet")
def nhan_du_lieu_nhiet(du_lieu_vao: DuLieuNhietVao):
    """Nhận dữ liệu nhiệt từ thiết bị."""
    hop_le, danh_sach_loi = kiem_tra_du_lieu(du_lieu_vao)
    if not hop_le:
        phan_hoi = ErrorResponse(
            trang_thai="error",
            thong_diep="Dữ liệu không hợp lệ",
            loi=danh_sach_loi,
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=phan_hoi.model_dump(by_alias=True))

    thoi_gian_server = datetime.now(timezone.utc)
    du_lieu_ra = DuLieuNhietRa(
        cam_bien_id=du_lieu_vao.cam_bien_id,
        thiet_bi_id=du_lieu_vao.thiet_bi_id,
        nhiet_do=du_lieu_vao.nhiet_do,
        do_am=du_lieu_vao.do_am,
        thoi_gian_thiet_bi=du_lieu_vao.thoi_gian_thiet_bi,
        thoi_gian_server=thoi_gian_server,
    )

    item_payload = du_lieu_ra.model_dump(by_alias=True, mode="json")
    try:
        save_reading(item_payload)
    except Exception as loi:
        logger.exception("Loi ghi Firebase: %s", loi)
        phan_hoi = ErrorResponse(
            trang_thai="error",
            thong_diep="Loi ghi du lieu",
            loi=[{"message": str(loi)}],
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=phan_hoi.model_dump(by_alias=True))

    alert_out: Optional[AlertOut] = None
    try:
        danh_sach = get_recent_readings(sensor_id=du_lieu_vao.cam_bien_id, limit=100)
        nhiet_do_list = [item.get("temp") for item in danh_sach if item.get("temp") is not None]
        trung_binh = tinh_trung_binh(nhiet_do_list)
        canh_bao, percent, muc_do = xu_ly_canh_bao(nhiet_do_list, du_lieu_vao.nhiet_do)
        if canh_bao:
            alert_out = AlertOut(
                cam_bien_id=du_lieu_vao.cam_bien_id,
                nhiet_do_tb=trung_binh,
                nhiet_do_hien_tai=du_lieu_vao.nhiet_do,
                phan_tram_tang=percent,
                nguong_tang=NGUONG_CANH_BAO,
                muc_do=muc_do,
                thoi_gian_tao=thoi_gian_server,
            )
            save_alert(alert_out.model_dump(by_alias=True, mode="json"))
    except Exception as loi:
        logger.exception("Loi tinh canh bao: %s", loi)

    payload: dict = {"item": item_payload}
    if alert_out is not None:
        payload["alert"] = alert_out.model_dump(by_alias=True, mode="json")

    phan_hoi = ApiResponse(
        trang_thai="success",
        thong_diep="Da nhan du lieu",
        du_lieu=payload,
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=phan_hoi.model_dump(by_alias=True))


@router.get("/api/du-lieu-nhiet")
def lay_du_lieu_nhiet(sensor_id: Optional[str] = None, limit: int = 50):
    """Lấy danh sách dữ liệu gần nhất."""
    try:
        danh_sach = get_recent_readings(sensor_id=sensor_id, limit=limit)
        items = [
            DuLieuNhietRa.model_validate(item).model_dump(by_alias=True, mode="json")
            for item in danh_sach
        ]
    except Exception as loi:
        logger.exception("Loi lay du lieu nhiet: %s", loi)
        phan_hoi = ErrorResponse(
            trang_thai="error",
            thong_diep="Loi lay du lieu",
            loi=[{"message": str(loi)}],
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=phan_hoi.model_dump(by_alias=True))

    phan_hoi = ApiResponse(
        trang_thai="success",
        thong_diep="OK",
        du_lieu={"items": items},
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=phan_hoi.model_dump(by_alias=True))


@router.get("/api/canh-bao")
def lay_canh_bao(sensor_id: Optional[str] = None, limit: int = 50):
    """Lấy danh sách cảnh báo gần nhất."""
    try:
        danh_sach = get_recent_alerts(sensor_id=sensor_id, limit=limit)
        items = [
            AlertOut.model_validate(item).model_dump(by_alias=True, mode="json")
            for item in danh_sach
        ]
    except Exception as loi:
        logger.exception("Loi lay canh bao: %s", loi)
        phan_hoi = ErrorResponse(
            trang_thai="error",
            thong_diep="Loi lay canh bao",
            loi=[{"message": str(loi)}],
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=phan_hoi.model_dump(by_alias=True))

    phan_hoi = ApiResponse(
        trang_thai="success",
        thong_diep="OK",
        du_lieu={"items": items},
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=phan_hoi.model_dump(by_alias=True))


@router.get("/api/trang-thai")
def trang_thai():
    """Kiểm tra trạng thái server."""
    phan_hoi = ApiResponse(
        trang_thai="ok",
        thong_diep="Đang hoạt động",
        du_lieu={"server_ts": datetime.now(timezone.utc).isoformat()},
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=phan_hoi.model_dump(by_alias=True))