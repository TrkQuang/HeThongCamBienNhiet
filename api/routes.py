from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from .schemas import DuLieuNhietVao, DuLieuNhietRa, AlertOut, ApiResponse, ErrorResponse
from core.processor import xu_ly_du_lieu
from database.db import SessionLocal
from database.repository import get_recent_readings, get_alerts
from utils.logger import logger
from utils.validators import kiem_tra_du_lieu

nhom_api = Blueprint("api", __name__)


def _lay_json() -> dict:
    """Lấy JSON từ request, trả về dict rỗng nếu không có."""
    return request.get_json(silent=True) or {}


@nhom_api.route("/api/du-lieu-nhiet", methods=["POST"])
def nhan_du_lieu_nhiet():
    """Nhận dữ liệu nhiệt từ thiết bị."""
    du_lieu_json = _lay_json()  # Dữ liệu JSON từ client
    try:
        du_lieu_vao = DuLieuNhietVao.model_validate(du_lieu_json)
    except ValidationError as loi:
        phan_hoi = ErrorResponse(
            trang_thai="error",
            thong_diep="Payload không hợp lệ",
            loi=loi.errors(),
        )
        return jsonify(phan_hoi.model_dump(by_alias=True)), 422

    hop_le, danh_sach_loi = kiem_tra_du_lieu(du_lieu_vao)
    if not hop_le:
        phan_hoi = ErrorResponse(
            trang_thai="error",
            thong_diep="Dữ liệu không hợp lệ",
            loi=danh_sach_loi,
        )
        return jsonify(phan_hoi.model_dump(by_alias=True)), 422

    db = SessionLocal()
    try:
        du_lieu_ra, alert_out = xu_ly_du_lieu(du_lieu_vao, db)  # Gọi core xử lý
    except Exception as loi:
        logger.exception("Loi xu ly du lieu: %s", loi)
        phan_hoi = ErrorResponse(
            trang_thai="error",
            thong_diep="Loi xu ly du lieu",
            loi=[{"message": str(loi)}],
        )
        return jsonify(phan_hoi.model_dump(by_alias=True)), 500
    finally:
        db.close()

    payload: dict = {"item": du_lieu_ra.model_dump(by_alias=True)}
    if alert_out is not None:
        payload["alert"] = alert_out.model_dump(by_alias=True)

    phan_hoi = ApiResponse(
        trang_thai="success",
        thong_diep="Da nhan du lieu",
        du_lieu=payload,
    )
    return jsonify(phan_hoi.model_dump(by_alias=True)), 201


@nhom_api.route("/api/du-lieu-nhiet", methods=["GET"])
def lay_du_lieu_nhiet():
    """Lấy danh sách dữ liệu gần nhất."""
    sensor_id = request.args.get("sensor_id")
    try:
        limit = int(request.args.get("limit", "50"))
    except ValueError:
        limit = 50

    db = SessionLocal()
    try:
        danh_sach = get_recent_readings(db, sensor_id=sensor_id, limit=limit)
        items = [
            DuLieuNhietRa(
                cam_bien_id=item.sensor_id,
                thiet_bi_id=item.device_id,
                nhiet_do=item.nhiet_do,
                do_am=item.do_am,
                thoi_gian_thiet_bi=item.thoi_gian_thiet_bi,
                thoi_gian_server=item.thoi_gian_server,
            ).model_dump(by_alias=True)
            for item in danh_sach
        ]
    finally:
        db.close()

    phan_hoi = ApiResponse(
        trang_thai="success",
        thong_diep="OK",
        du_lieu={"items": items},
    )
    return jsonify(phan_hoi.model_dump(by_alias=True)), 200


@nhom_api.route("/api/canh-bao", methods=["GET"])
def lay_canh_bao():
    """Lấy danh sách cảnh báo gần nhất."""
    sensor_id = request.args.get("sensor_id")
    try:
        limit = int(request.args.get("limit", "50"))
    except ValueError:
        limit = 50

    db = SessionLocal()
    try:
        danh_sach = get_alerts(db, sensor_id=sensor_id, limit=limit)
        items = [
            AlertOut(
                cam_bien_id=item.sensor_id,
                nhiet_do_tb=item.nhiet_do_tb,
                nhiet_do_hien_tai=item.nhiet_do_hien_tai,
                phan_tram_tang=item.phan_tram_tang,
                nguong_tang=item.nguong,
                muc_do=item.muc_do,
                thoi_gian_tao=item.tao_luc,
            ).model_dump(by_alias=True)
            for item in danh_sach
        ]
    finally:
        db.close()

    phan_hoi = ApiResponse(
        trang_thai="success",
        thong_diep="OK",
        du_lieu={"items": items},
    )
    return jsonify(phan_hoi.model_dump(by_alias=True)), 200


@nhom_api.route("/api/trang-thai", methods=["GET"])
def trang_thai():
    """Kiểm tra trạng thái server."""
    phan_hoi = ApiResponse(
        trang_thai="ok",
        thong_diep="Đang hoạt động",
        du_lieu={"server_ts": datetime.now(timezone.utc).isoformat()},
    )
    return jsonify(phan_hoi.model_dump(by_alias=True)), 200