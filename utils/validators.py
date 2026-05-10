from datetime import datetime, timezone, timedelta

from api.schemas import DuLieuNhietVao


def kiem_tra_du_lieu(du_lieu_vao: DuLieuNhietVao) -> tuple[bool, list[dict]]:
	"""Kiểm tra dữ liệu đầu vào theo quy tắc cơ bản."""
	danh_sach_loi: list[dict] = []

	if not du_lieu_vao.cam_bien_id:
		danh_sach_loi.append({"truong": "sensor_id", "loi": "Thiếu mã cảm biến"})

	if not du_lieu_vao.thiet_bi_id:
		danh_sach_loi.append({"truong": "device_id", "loi": "Thiếu mã thiết bị"})

	if du_lieu_vao.nhiet_do < -40 or du_lieu_vao.nhiet_do > 125:
		danh_sach_loi.append({"truong": "temp", "loi": "Nhiệt độ ngoài phạm vi"})

	if du_lieu_vao.do_am is not None:
		if du_lieu_vao.do_am < 0 or du_lieu_vao.do_am > 100:
			danh_sach_loi.append({"truong": "humidity", "loi": "Độ ẩm ngoài phạm vi"})

	if du_lieu_vao.thoi_gian_thiet_bi is not None:
		gio_hien_tai = datetime.now(timezone.utc)
		gio_toi_da = gio_hien_tai + timedelta(minutes=5)
		if du_lieu_vao.thoi_gian_thiet_bi > gio_toi_da:
			danh_sach_loi.append({"truong": "ts", "loi": "Thời gian thiết bị không hợp lệ"})

	hop_le = len(danh_sach_loi) == 0
	return hop_le, danh_sach_loi
