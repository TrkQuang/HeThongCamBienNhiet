from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from .schemas import DuLieuNhietVao, ApiResponse, ErrorResponse
from core.processor import xu_ly_du_lieu
from utils.validators import kiem_tra_du_lieu

nhom_api = Blueprint("api", __name__)
du_lieu_tam: list[dict] = []  # Lưu tạm dữ liệu gần nhất để demo


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

    du_lieu_ra = xu_ly_du_lieu(du_lieu_vao)  # Gọi core xử lý
    du_lieu_tam.append(du_lieu_ra.model_dump(by_alias=True))

    if len(du_lieu_tam) > 1000:
        du_lieu_tam.pop(0)  # Giữ bộ nhớ ổn định

    phan_hoi = ApiResponse(
        trang_thai="success",
        thong_diep="Đã nhận dữ liệu",
        du_lieu={"item": du_lieu_ra.model_dump(by_alias=True)},
    )
    return jsonify(phan_hoi.model_dump(by_alias=True)), 201


@nhom_api.route("/api/du-lieu-nhiet", methods=["GET"])
def lay_du_lieu_nhiet():
    """Lấy danh sách dữ liệu gần nhất."""
    phan_hoi = ApiResponse(
        trang_thai="success",
        thong_diep="OK",
        du_lieu={"items": du_lieu_tam[-50:]},
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