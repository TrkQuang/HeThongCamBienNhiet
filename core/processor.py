from datetime import datetime, timezone

from api.schemas import DuLieuNhietVao, DuLieuNhietRa


def xu_ly_du_lieu(du_lieu_vao: DuLieuNhietVao) -> DuLieuNhietRa:
	"""Chuẩn hóa dữ liệu và gắn thời gian server."""
	thoi_gian_server = datetime.now(timezone.utc)  # Thời gian ghi nhận tại server
	du_lieu_ra = DuLieuNhietRa(
		cam_bien_id=du_lieu_vao.cam_bien_id,
		nhiet_do=du_lieu_vao.nhiet_do,
		do_am=du_lieu_vao.do_am,
		thoi_gian_thiet_bi=du_lieu_vao.thoi_gian_thiet_bi,
		thoi_gian_server=thoi_gian_server,
	)
	return du_lieu_ra
