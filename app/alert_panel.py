"""
Bang canh bao nhiet do - giao dien hien dai
"""

import threading
from typing import Optional
import customtkinter as ctk
from datetime import datetime

from .api_client import ApiClient
from .settings_store import AppSettings
from core.ai_suggester import tao_goi_y_ha_nhiet
from .widgets import (
	MAU_NEN_SANG,
	MAU_THE_BG,
	MAU_CHU_CHINH,
	MAU_CHU_PHU,
	MAU_DUONG_BIEN,
	MAU_CANH_BAO,
	MAU_NGUY_HIEM,
	MAU_THANH_CONG,
	FONT_TIEU_DE,
	FONT_NHAN,
	FONT_TIEU_DE_THE,
	FONT_NOI_DUNG,
	FONT_NOI_DUNG_BOLD,
	FONT_SO_LON,
	The,
	HuyHieu,
	mau_theo_nhiet_do,
	mau_theo_muc,
)


class AlertView(ctk.CTkFrame):
	def __init__(self, parent, api_client: ApiClient, settings: AppSettings):
		super().__init__(parent, fg_color=MAU_NEN_SANG)
		self._api_client = api_client
		self._settings = settings
		self._refresh_ms = max(settings.refresh_ms, 1000)
		self._sensor_id = settings.sensor_id.strip() or None
		self._dang_cap_nhat = False
		self._after_id = None

		self.du_lieu = self.tao_du_lieu_mau()

		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.tao_noi_dung()
		self.cap_nhat_du_lieu()

	def tao_du_lieu_mau(self):
		return {
			"nhiet_do_hien_tai": 36,
			"do_am": 62,
			"nguong_canh_bao": 35,
			"nguong_nguy_hiem": 40,
			"muc_do": "Cảnh báo",
			"ghi_chu": "Nóng, rực lửa",
			"vi_tri": "Kho lạnh A1",
			"cam_bien": "SENSOR-02",
			"nguy_co": [
				"Tăng tốc độ lão hóa linh kiện",
				"Hư hỏng dàn lạnh nếu kéo dài",
				"Nguy cơ cháy cầu chì nguồn",
			],
			"goi_y": [
				"Tăng lưu lượng quạt gió",
				"Kiểm tra dàn nóng và vệ sinh lọc bụi",
				"Giảm tải trong 30 phút",
			],
			"lich_su": [
				{
					"thoi_gian": "08:20",
					"nhiet_do": 31,
					"muc": "normal",
					"ghi_chu": "Ổn định",
				},
				{
					"thoi_gian": "09:10",
					"nhiet_do": 34,
					"muc": "warning",
					"ghi_chu": "Tiệm cận ngưỡng",
				},
				{
					"thoi_gian": "10:05",
					"nhiet_do": 36,
					"muc": "warning",
					"ghi_chu": "Vượt ngưỡng cảnh báo",
				},
				{
					"thoi_gian": "10:40",
					"nhiet_do": 38,
					"muc": "warning",
					"ghi_chu": "Nhiệt tăng liên tục",
				},
				{
					"thoi_gian": "11:15",
					"nhiet_do": 41,
					"muc": "danger",
					"ghi_chu": "Nguy cơ quá nhiệt",
				},
			],
		}

	def tao_noi_dung(self):
		khung_chinh = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
		khung_chinh.grid(row=0, column=0, sticky="nsew")
		khung_chinh.grid_rowconfigure(0, weight=0)
		khung_chinh.grid_rowconfigure(1, weight=1)
		khung_chinh.grid_columnconfigure(0, weight=1)

		self.tao_tieu_de(khung_chinh)

		khung_noi_dung = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
		khung_noi_dung.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
		khung_noi_dung.grid_rowconfigure(0, weight=0)
		khung_noi_dung.grid_rowconfigure(1, weight=1)
		khung_noi_dung.grid_columnconfigure(0, weight=1)

		khung_tren = ctk.CTkFrame(khung_noi_dung, fg_color=MAU_NEN_SANG)
		khung_tren.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
		khung_tren.grid_columnconfigure(0, weight=2)
		khung_tren.grid_columnconfigure(1, weight=1)

		self.tao_the_trang_thai(khung_tren)
		self.tao_cot_goi_y(khung_tren)
		self.tao_the_lich_su(khung_noi_dung)

	def tao_tieu_de(self, cha):
		tieu_de = ctk.CTkFrame(cha, fg_color=MAU_NEN_SANG, corner_radius=0)
		tieu_de.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
		tieu_de.grid_columnconfigure(0, weight=1)

		nhan_tieu_de = ctk.CTkLabel(
			tieu_de,
			text="Cảnh Báo",
			font=FONT_TIEU_DE,
			text_color=MAU_CHU_CHINH,
		)
		nhan_tieu_de.pack(side="left", anchor="w")

		self.nhan_thoi_gian = ctk.CTkLabel(
			tieu_de,
			text=f"Cập nhật: {datetime.now().strftime('%d/%m/%Y • %H:%M')}",
			font=FONT_NHAN,
			text_color=MAU_CHU_PHU,
		)
		self.nhan_thoi_gian.pack(side="right", anchor="e")

	def tao_the_trang_thai(self, cha):
		the = The(cha)
		the.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

		trong = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
		trong.pack(fill="both", expand=True, padx=25, pady=25)

		nhan_tieu_de = ctk.CTkLabel(
			trong,
			text="Tình trạng hiện tại",
			font=FONT_TIEU_DE_THE,
			text_color=MAU_CHU_PHU,
		)
		nhan_tieu_de.pack(anchor="w", pady=(0, 10))

		self.nhan_nhiet_do = ctk.CTkLabel(
			trong,
			text=f"{self.du_lieu['nhiet_do_hien_tai']}°C",
			font=FONT_SO_LON,
			text_color=MAU_NGUY_HIEM,
		)
		self.nhan_nhiet_do.pack(anchor="w", pady=(0, 10))

		hang_muc_do = ctk.CTkFrame(trong, fg_color=MAU_THE_BG)
		hang_muc_do.pack(fill="x", pady=(0, 10))

		self.nhan_ghi_chu = ctk.CTkLabel(
			hang_muc_do,
			text=f"Ghi chú: {self.du_lieu['ghi_chu']}",
			font=FONT_NOI_DUNG,
			text_color=MAU_CHU_CHINH,
		)
		self.nhan_ghi_chu.pack(side="left")

		self.huy_hieu = HuyHieu(hang_muc_do, text=self.du_lieu["muc_do"].upper(), mau=MAU_CANH_BAO)
		self.huy_hieu.pack(side="right")

		duong_ngan = ctk.CTkFrame(trong, height=1, fg_color=MAU_DUONG_BIEN)
		duong_ngan.pack(fill="x", pady=15)

		self.nhan_cam_bien = self.tao_hang_thong_tin(trong, "Cảm biến:", self.du_lieu["cam_bien"])
		self.nhan_vi_tri = self.tao_hang_thong_tin(trong, "Vị trí:", self.du_lieu["vi_tri"])
		self.nhan_do_am = self.tao_hang_thong_tin(trong, "Độ ẩm:", f"{self.du_lieu['do_am']}%")
		self.nhan_nguong = self.tao_hang_thong_tin(
			trong,
			"Ngưỡng cảnh báo:",
			f"{self.du_lieu['nguong_canh_bao']}°C",
			MAU_CANH_BAO,
		)

		duong_ngan_2 = ctk.CTkFrame(trong, height=1, fg_color=MAU_DUONG_BIEN)
		duong_ngan_2.pack(fill="x", pady=15)

		khung_tien_trinh = ctk.CTkFrame(trong, fg_color=MAU_THE_BG)
		khung_tien_trinh.pack(fill="x")

		nhan_tien_trinh = ctk.CTkLabel(
			khung_tien_trinh,
			text="Mức độ nhiệt:",
			font=FONT_NOI_DUNG,
			text_color=MAU_CHU_PHU,
		)
		nhan_tien_trinh.pack(anchor="w")

		self.tien_trinh = ctk.CTkProgressBar(
			khung_tien_trinh,
			fg_color=MAU_DUONG_BIEN,
			progress_color=MAU_NGUY_HIEM,
			height=8,
			corner_radius=4,
		)
		self.tien_trinh.pack(fill="x", pady=(8, 0))
		self.tien_trinh.set(min(self.du_lieu["nhiet_do_hien_tai"] / 45.0, 1.0))

	def tao_hang_thong_tin(self, cha, nhan, gia_tri, mau=None):
		hang = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
		hang.pack(fill="x", pady=4)

		nhan_trai = ctk.CTkLabel(
			hang,
			text=nhan,
			font=FONT_NOI_DUNG,
			text_color=MAU_CHU_PHU,
		)
		nhan_trai.pack(side="left")

		nhan_phai = ctk.CTkLabel(
			hang,
			text=gia_tri,
			font=FONT_NOI_DUNG_BOLD,
			text_color=mau or MAU_CHU_CHINH,
		)
		nhan_phai.pack(side="right")

		return nhan_phai

	def tao_cot_goi_y(self, cha):
		cot = ctk.CTkFrame(cha, fg_color=MAU_NEN_SANG)
		cot.grid(row=0, column=1, sticky="nsew")
		cot.grid_rowconfigure(0, weight=0)
		cot.grid_rowconfigure(1, weight=0)
		cot.grid_columnconfigure(0, weight=1)

		self.khung_nguy_co = self.tao_the_danh_sach(
			cot,
			0,
			"Cảnh báo nguy cơ",
			self.du_lieu["nguy_co"],
			MAU_NGUY_HIEM,
		)
		self.khung_goi_y = self.tao_the_danh_sach(
			cot,
			1,
			"Gợi ý giải pháp",
			self.du_lieu["goi_y"],
			MAU_THANH_CONG,
		)

	def tao_the_danh_sach(self, cha, dong, tieu_de, danh_sach, mau):
		the = The(cha)
		the.grid(row=dong, column=0, sticky="nsew", pady=(0, 15))

		khung = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
		khung.pack(fill="both", expand=True, padx=20, pady=20)

		nhan_tieu_de = ctk.CTkLabel(
			khung,
			text=tieu_de,
			font=FONT_TIEU_DE_THE,
			text_color=MAU_CHU_CHINH,
		)
		nhan_tieu_de.pack(anchor="w", pady=(0, 10))

		self.cap_nhat_danh_sach(khung, danh_sach, mau)
		return khung

	def cap_nhat_danh_sach(self, khung, danh_sach, mau):
		for child in khung.winfo_children():
			child.destroy()

		for muc in danh_sach:
			hang = ctk.CTkFrame(khung, fg_color=MAU_THE_BG)
			hang.pack(fill="x", pady=6)

			cham = ctk.CTkLabel(
				hang,
				text="•",
				font=FONT_NOI_DUNG_BOLD,
				text_color=mau,
				width=14,
			)
			cham.pack(side="left")

			nhan = ctk.CTkLabel(
				hang,
				text=muc,
				font=FONT_NOI_DUNG,
				text_color=MAU_CHU_PHU,
			)
			nhan.pack(side="left")

	def tao_the_lich_su(self, cha):
		the = The(cha)
		the.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
		the.grid_rowconfigure(1, weight=1)
		the.grid_columnconfigure(0, weight=1)

		nhan_tieu_de = ctk.CTkLabel(
			the,
			text="Cảnh báo theo thời gian",
			font=FONT_TIEU_DE_THE,
			text_color=MAU_CHU_CHINH,
		)
		nhan_tieu_de.pack(anchor="w", padx=25, pady=(20, 10))

		self.khung_lich_su = ctk.CTkScrollableFrame(the, fg_color=MAU_THE_BG)
		self.khung_lich_su.pack(fill="both", expand=True, padx=20, pady=(0, 20))
		self.cap_nhat_lich_su(self.du_lieu["lich_su"])

	def cap_nhat_cau_hinh(self, settings: AppSettings) -> None:
		self._settings = settings
		self._sensor_id = settings.sensor_id.strip() or None
		self._refresh_ms = max(settings.refresh_ms, 1000)

	def cap_nhat_du_lieu(self) -> None:
		if self._dang_cap_nhat:
			self._lap_lich_cap_nhat()
			return

		self._dang_cap_nhat = True
		thread = threading.Thread(target=self._tai_du_lieu, daemon=True)
		thread.start()

	def _lap_lich_cap_nhat(self) -> None:
		if self._after_id is not None:
			self.after_cancel(self._after_id)
		self._after_id = self.after(self._refresh_ms, self.cap_nhat_du_lieu)

	def _tai_du_lieu(self) -> None:
		alerts = None
		readings = None
		error = None
		try:
			alerts = self._api_client.get_alerts(sensor_id=self._sensor_id, limit=10)
			readings = self._api_client.get_readings(sensor_id=self._sensor_id, limit=5)
		except Exception as exc:
			error = str(exc)

		self.after(0, lambda: self._cap_nhat_du_lieu_ui(alerts, readings, error))

	def _cap_nhat_du_lieu_ui(self, alerts, readings, error) -> None:
		if alerts:
			latest = alerts[0]
			current_temp = latest.get("current_temp")
			level = latest.get("level", "")
			threshold = latest.get("threshold")
			avg_temp = latest.get("avg_temp")
			created_at = latest.get("created_at")

			if current_temp is not None:
				self.nhan_nhiet_do.configure(text=f"{float(current_temp):.1f}°C")
				self.tien_trinh.set(min(float(current_temp) / 45.0, 1.0))

			mau_muc = mau_theo_muc(level)
			self.huy_hieu.configure(text=level.upper() or "ALERT", fg_color=mau_muc)
			self.nhan_ghi_chu.configure(text=self._ghi_chu(level, current_temp))

			nguong_text = f"{float(threshold):.1f}°C" if threshold is not None else "--"
			self.nhan_nguong.configure(text=nguong_text, text_color=mau_muc)

			cam_bien = latest.get("sensor_id") or self._sensor_id or "--"
			self.nhan_cam_bien.configure(text=cam_bien)
			self.nhan_vi_tri.configure(text=f"Sensor {cam_bien}")

			goi_y = tao_goi_y_ha_nhiet(float(current_temp or 0), float(avg_temp or 0), float(threshold or 0))
			self.cap_nhat_danh_sach(self.khung_goi_y, [goi_y], MAU_THANH_CONG)
			self.cap_nhat_danh_sach(self.khung_nguy_co, self._nguy_co(level), MAU_NGUY_HIEM)

			self.cap_nhat_lich_su(self._doi_lich_su(alerts))

			if created_at:
				self.nhan_thoi_gian.configure(text=f"Cập nhật: {self._dinh_dang_ngay(created_at)}")

		if readings:
			latest_reading = readings[0]
			do_am = latest_reading.get("humidity")
			if do_am is not None:
				self.nhan_do_am.configure(text=f"{float(do_am):.0f}%")

		if error:
			self._lap_lich_cap_nhat()
		else:
			self._lap_lich_cap_nhat()

		self._dang_cap_nhat = False

	def _dinh_dang_ngay(self, raw_ts: str) -> str:
		try:
			dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
			return dt.strftime("%d/%m/%Y • %H:%M")
		except ValueError:
			return datetime.now().strftime("%d/%m/%Y • %H:%M")

	def _ghi_chu(self, level: str, temp: Optional[float]) -> str:
		if not level:
			return "Ghi chú: Ổn định"
		if str(level).lower() in {"danger", "high"}:
			return "Ghi chú: Nguy cơ quá nhiệt"
		if str(level).lower() in {"warning", "warn"}:
			return "Ghi chú: Vượt ngưỡng cảnh báo"
		if temp is not None:
			return f"Ghi chú: {float(temp):.1f}°C"
		return "Ghi chú: Đang theo dõi"

	def _nguy_co(self, level: str) -> list[str]:
		level = str(level).lower()
		if level in {"danger", "high"}:
			return [
				"Nhiệt vượt ngưỡng nguy hiểm",
				"Nguy cơ hỏng thiết bị",
				"Cần xử lý ngay",
			]
		if level in {"warning", "warn"}:
			return [
				"Nhiệt vượt ngưỡng cảnh báo",
				"Theo dõi liên tục",
			]
		return ["Hệ thống đang ổn định"]

	def _doi_lich_su(self, alerts) -> list[dict]:
		lich_su = []
		for item in alerts:
			created_at = item.get("created_at")
			gio = self._dinh_dang_ngay(created_at) if created_at else "--"
			muc = item.get("level", "normal")
			ghi_chu = self._ghi_chu(muc, item.get("current_temp"))
			lich_su.append(
				{
					"thoi_gian": gio.split(" • ")[-1],
					"nhiet_do": item.get("current_temp", 0),
					"muc": muc,
					"ghi_chu": ghi_chu.replace("Ghi chú: ", ""),
				}
			)
		return lich_su

	def cap_nhat_lich_su(self, lich_su):
		for child in self.khung_lich_su.winfo_children():
			child.destroy()

		for muc in lich_su:
			dong = ctk.CTkFrame(self.khung_lich_su, fg_color=MAU_THE_BG)
			dong.pack(fill="x", pady=10)

			nhan_gio = ctk.CTkLabel(
				dong,
				text=muc["thoi_gian"],
				font=FONT_NOI_DUNG_BOLD,
				text_color=MAU_CHU_CHINH,
				width=60,
			)
			nhan_gio.pack(side="left", padx=(0, 15))

			khung_thong_tin = ctk.CTkFrame(dong, fg_color=MAU_THE_BG)
			khung_thong_tin.pack(side="left", fill="x", expand=True)

			mau_muc = mau_theo_muc(muc["muc"])
			huy_hieu = HuyHieu(khung_thong_tin, text=str(muc["muc"]).upper(), mau=mau_muc)
			huy_hieu.pack(anchor="w")

			nhan_ghi_chu = ctk.CTkLabel(
				khung_thong_tin,
				text=muc["ghi_chu"],
				font=FONT_NOI_DUNG,
				text_color=MAU_CHU_PHU,
			)
			nhan_ghi_chu.pack(anchor="w")

			nhiet_do = float(muc.get("nhiet_do", 0))
			nhan_nhiet_do = ctk.CTkLabel(
				dong,
				text=f"{nhiet_do:.1f}°C",
				font=FONT_NOI_DUNG_BOLD,
				text_color=mau_theo_nhiet_do(nhiet_do),
				width=60,
			)
			nhan_nhiet_do.pack(side="right", padx=10)

			tien_trinh = ctk.CTkProgressBar(
				dong,
				fg_color=MAU_DUONG_BIEN,
				progress_color=mau_muc,
				height=6,
				corner_radius=3,
				width=120,
			)
			tien_trinh.pack(side="right", padx=10)
			tien_trinh.set(min(nhiet_do / 45.0, 1.0))


__all__ = ["AlertView"]
