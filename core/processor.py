from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from api.schemas import DuLieuNhietVao, DuLieuNhietRa, AlertOut
from core.aggregator import tinh_trung_binh, xu_ly_canh_bao
from core.thresholds import NGUONG_CANH_BAO
from database.repository import save_reading, get_recent_readings, save_alert


def xu_ly_du_lieu(du_lieu_vao: DuLieuNhietVao, db: Optional[Session] = None) -> Tuple[DuLieuNhietRa, Optional[AlertOut]]:
	"""Chuẩn hóa dữ liệu, lưu DB, tính cảnh báo (nếu có)."""
	thoi_gian_server = datetime.now(timezone.utc)  # Thời gian ghi nhận tại server
	du_lieu_ra = DuLieuNhietRa(
		cam_bien_id=du_lieu_vao.cam_bien_id,
		thiet_bi_id=du_lieu_vao.thiet_bi_id,
		nhiet_do=du_lieu_vao.nhiet_do,
		do_am=du_lieu_vao.do_am,
		thoi_gian_thiet_bi=du_lieu_vao.thoi_gian_thiet_bi,
		thoi_gian_server=thoi_gian_server,
	)

	alert_out: Optional[AlertOut] = None
	if db is not None:
		save_reading(
			db,
			sensor_id=du_lieu_vao.cam_bien_id,
			device_id=du_lieu_vao.thiet_bi_id,
			temp=du_lieu_vao.nhiet_do,
			humidity=du_lieu_vao.do_am,
			device_ts=du_lieu_vao.thoi_gian_thiet_bi,
		)

		danh_sach = get_recent_readings(db, sensor_id=du_lieu_vao.cam_bien_id, limit=100)
		nhiet_do_list = [item.nhiet_do for item in danh_sach if item.nhiet_do is not None]
		trung_binh = tinh_trung_binh(nhiet_do_list)
		canh_bao, percent, muc_do = xu_ly_canh_bao(nhiet_do_list, du_lieu_vao.nhiet_do)
		if canh_bao:
			alert = save_alert(
				db,
				sensor_id=du_lieu_vao.cam_bien_id,
				avg_temp=trung_binh,
				current_temp=du_lieu_vao.nhiet_do,
				percent=percent,
				threshold=NGUONG_CANH_BAO,
				level=muc_do,
			)
			alert_out = AlertOut(
				cam_bien_id=alert.sensor_id,
				nhiet_do_tb=alert.nhiet_do_tb,
				nhiet_do_hien_tai=alert.nhiet_do_hien_tai,
				phan_tram_tang=alert.phan_tram_tang,
				nguong_tang=alert.nguong,
				muc_do=alert.muc_do,
				thoi_gian_tao=alert.tao_luc,
			)

	return du_lieu_ra, alert_out
