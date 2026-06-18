"""Temperature data, alerts, and AI suggestion routes."""

from datetime import datetime, timezone

from fastapi import APIRouter

from core.ai_suggester import tao_goi_y_ha_nhiet
from core.aggregator import tinh_trung_binh, xu_ly_canh_bao
from core.thresholds import NGUONG_CANH_BAO
from firebase.alert_repo import get_recent_alerts, save_alert
from firebase.sensor_repo import get_recent_readings, save_reading
from utils.logger import logger
from utils.validators import kiem_tra_du_lieu

from .schemas import AlertOut, AiSuggestionRequest, DuLieuNhietRa, DuLieuNhietVao
from .utils import res_err, res_ok

router = APIRouter()


# ==================================================
# Nhận dữ liệu nhiệt độ từ thiết bị
# ==================================================
@router.post("/api/du-lieu-nhiet")
def nhan_du_lieu_nhiet(du_lieu: DuLieuNhietVao):
    hop_le, loi = kiem_tra_du_lieu(du_lieu)
    if not hop_le:
        return res_err("Dữ liệu không hợp lệ", 422, loi)

    du_lieu_ra = DuLieuNhietRa(
        thiet_bi_id=du_lieu.thiet_bi_id,
        nhiet_do=du_lieu.nhiet_do,
        do_am=du_lieu.do_am,
        thoi_gian_thiet_bi=du_lieu.thoi_gian_thiet_bi,
        thoi_gian_server=datetime.now(timezone.utc),
    )

    try:
        save_reading(du_lieu.thiet_bi_id, du_lieu_ra.model_dump(by_alias=True, mode="json"))
    except Exception as e:
        logger.exception("Lỗi ghi dữ liệu: %s", e)
        return res_err("Lỗi cơ sở dữ liệu", 500)

    # Kiểm tra cảnh báo tự động
    canh_bao = None
    try:
        danh_sach_doc = get_recent_readings(du_lieu.thiet_bi_id, limit=100)
        danh_sach_nhiet_do = [r.get("temp") for r in danh_sach_doc if r.get("temp") is not None]
        canh_bao_bat, phan_tram_tang, muc_do = xu_ly_canh_bao(danh_sach_nhiet_do, du_lieu.nhiet_do)
        if canh_bao_bat:
            canh_bao = AlertOut(
                thiet_bi_id=du_lieu.thiet_bi_id,
                nhiet_do_tb=tinh_trung_binh(danh_sach_nhiet_do),
                nhiet_do_hien_tai=du_lieu.nhiet_do,
                phan_tram_tang=phan_tram_tang,
                nguong_tang=NGUONG_CANH_BAO,
                muc_do=muc_do,
                thoi_gian_tao=datetime.now(timezone.utc),
            )
            save_alert(du_lieu.thiet_bi_id, canh_bao.model_dump(by_alias=True, mode="json"))
    except Exception as e:
        logger.exception("Lỗi xử lý cảnh báo: %s", e)

    return res_ok(
        {"item": du_lieu_ra.model_dump(by_alias=True, mode="json"), "alert": canh_bao.model_dump(by_alias=True, mode="json") if canh_bao else None},
        "Đã nhận dữ liệu",
        201,
    )


# ==================================================
# Lấy lịch sử dữ liệu nhiệt độ
# ==================================================
@router.get("/api/du-lieu-nhiet")
def lay_du_lieu_nhiet(device_id: str = None, limit: int = 50):
    if not device_id:
        return res_err("Thiếu device_id")

    try:
        danh_sach = [
            DuLieuNhietRa.model_validate(r).model_dump(by_alias=True, mode="json")
            for r in get_recent_readings(device_id, limit)
        ]
        return res_ok({"items": danh_sach})
    except Exception as e:
        logger.exception("Lỗi đọc dữ liệu: %s", e)
        return res_err("Lỗi đọc dữ liệu", 500)


# ==================================================
# Lấy danh sách cảnh báo
# ==================================================
@router.get("/api/alerts")
def lay_canh_bao(device_id: str = None, limit: int = 50):
    if not device_id:
        return res_err("Thiếu device_id")

    try:
        danh_sach = [
            AlertOut.model_validate(r).model_dump(by_alias=True, mode="json")
            for r in get_recent_alerts(device_id, limit)
            if isinstance(r, dict)
        ]
        return res_ok({"items": danh_sach})
    except Exception as e:
        logger.exception("Lỗi đọc cảnh báo: %s", e)
        return res_err("Lỗi đọc cảnh báo", 500)


# ==================================================
# Gợi ý AI giảm nhiệt
# ==================================================
@router.post("/api/ai/goi-y")
def lay_goi_y_ai(yeu_cau: AiSuggestionRequest):
    try:
        goi_y = tao_goi_y_ha_nhiet(yeu_cau.nhiet_do_hien_tai, yeu_cau.nhiet_do_trung_binh, yeu_cau.nguong)
        return res_ok({"suggestion": goi_y})
    except Exception as e:
        return res_err(str(e), 500)