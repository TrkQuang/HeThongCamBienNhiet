"""
Man hinh cai dat - giao dien hien dai
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable

from .settings_store import AppSettings

from .widgets import (
	MAU_NEN_SANG,
	MAU_THE_BG,
	MAU_CHINH,
	MAU_CHINH_HOVER,
	MAU_CHU_CHINH,
	MAU_CHU_PHU,
	MAU_DUONG_BIEN,
	FONT_TIEU_DE,
	FONT_TIEU_DE_THE,
	FONT_NOI_DUNG,
	FONT_NOI_DUNG_BOLD,
	The,
)


class SettingsView(ctk.CTkFrame):
	def __init__(self, parent, settings: AppSettings, on_save: Callable[[AppSettings], None]):
		super().__init__(parent, fg_color=MAU_NEN_SANG)
		self._on_save = on_save
		self._settings = settings

		self.nguong_canh_bao = tk.DoubleVar(value=settings.warning_threshold)
		self.nguong_nguy_hiem = tk.DoubleVar(value=settings.danger_threshold)
		self.nguong_do_am = tk.DoubleVar(value=settings.humidity_threshold)
		self.tan_suat_lay_mau = tk.IntVar(value=max(int(settings.refresh_ms / 1000), 1))
		self.api_url = tk.StringVar(value=settings.api_base_url)
		self.can_bao_am_thanh = tk.BooleanVar(value=settings.sound_alert)
		self.gui_email = tk.BooleanVar(value=settings.email_alert)

		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.tao_noi_dung()

	def tao_noi_dung(self):
		khung_chinh = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
		khung_chinh.grid(row=0, column=0, sticky="nsew")
		khung_chinh.grid_rowconfigure(0, weight=0)
		khung_chinh.grid_rowconfigure(1, weight=1)
		khung_chinh.grid_columnconfigure(0, weight=1)

		tieu_de = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
		tieu_de.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
		tieu_de.grid_columnconfigure(0, weight=1)

		nhan_tieu_de = ctk.CTkLabel(
			tieu_de,
			text="Cài đặt hệ thống",
			font=FONT_TIEU_DE,
			text_color=MAU_CHU_CHINH,
		)
		nhan_tieu_de.pack(side="left", anchor="w")

		khung_noi_dung = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
		khung_noi_dung.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
		khung_noi_dung.grid_rowconfigure(0, weight=1)
		khung_noi_dung.grid_columnconfigure(0, weight=1)
		khung_noi_dung.grid_columnconfigure(1, weight=1)

		self.tao_the_nhiet_do(khung_noi_dung)
		self.tao_the_ket_noi(khung_noi_dung)
		self.tao_khung_hanh_dong(khung_noi_dung)

	def tao_the_nhiet_do(self, cha):
		the = The(cha)
		the.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=(0, 15))

		khung = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
		khung.pack(fill="both", expand=True, padx=20, pady=20)

		nhan = ctk.CTkLabel(
			khung,
			text="Cấu hình ngưỡng",
			font=FONT_TIEU_DE_THE,
			text_color=MAU_CHU_CHINH,
		)
		nhan.pack(anchor="w", pady=(0, 15))

		self.tao_hang_slider(
			khung,
			"Ngưỡng cảnh báo (°C)",
			self.nguong_canh_bao,
			20,
			45,
		)
		self.tao_hang_slider(
			khung,
			"Ngưỡng nguy hiểm (°C)",
			self.nguong_nguy_hiem,
			30,
			55,
		)
		self.tao_hang_slider(
			khung,
			"Tần suất lấy mẫu (giây)",
			self.tan_suat_lay_mau,
			1,
			60,
			is_int=True,
		)

	def tao_hang_slider(self, cha, nhan, bien, min_val, max_val, is_int=False):
		khung = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
		khung.pack(fill="x", pady=10)

		nhan_trai = ctk.CTkLabel(
			khung,
			text=nhan,
			font=FONT_NOI_DUNG,
			text_color=MAU_CHU_PHU,
		)
		nhan_trai.pack(anchor="w")

		khung_gia_tri = ctk.CTkFrame(khung, fg_color=MAU_THE_BG)
		khung_gia_tri.pack(fill="x", pady=(6, 0))

		thanh_truot = ctk.CTkSlider(
			khung_gia_tri,
			from_=min_val,
			to=max_val,
			number_of_steps=(max_val - min_val) if is_int else None,
			command=lambda gia_tri: self.cap_nhat_slider(bien, gia_tri, nhan_gia_tri, is_int),
		)
		thanh_truot.pack(side="left", fill="x", expand=True, padx=(0, 10))
		thanh_truot.set(bien.get())

		nhan_gia_tri = ctk.CTkLabel(
			khung_gia_tri,
			text=str(int(bien.get()) if is_int else round(bien.get(), 1)),
			font=FONT_NOI_DUNG_BOLD,
			text_color=MAU_CHU_CHINH,
			width=60,
		)
		nhan_gia_tri.pack(side="right")

	def cap_nhat_slider(self, bien, gia_tri, nhan_gia_tri, is_int):
		gia_tri = int(gia_tri) if is_int else round(gia_tri, 1)
		bien.set(gia_tri)
		nhan_gia_tri.configure(text=str(gia_tri))

	def tao_the_ket_noi(self, cha):
		the = The(cha)
		the.grid(row=0, column=1, sticky="nsew", pady=(0, 15))

		khung = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
		khung.pack(fill="both", expand=True, padx=20, pady=20)

		nhan = ctk.CTkLabel(
			khung,
			text="Kết nối và thông báo",
			font=FONT_TIEU_DE_THE,
			text_color=MAU_CHU_CHINH,
		)
		nhan.pack(anchor="w", pady=(0, 15))

		self.tao_hang_entry(khung, "API URL", self.api_url)

		duong_ngan = ctk.CTkFrame(khung, height=1, fg_color=MAU_DUONG_BIEN)
		duong_ngan.pack(fill="x", pady=15)

		self.tao_hang_switch(khung, "Bật cảnh báo âm thanh", self.can_bao_am_thanh)
		self.tao_hang_switch(khung, "Gửi email khi nguy hiểm", self.gui_email)

	def tao_hang_entry(self, cha, nhan, bien):
		khung = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
		khung.pack(fill="x", pady=10)

		nhan_trai = ctk.CTkLabel(
			khung,
			text=nhan,
			font=FONT_NOI_DUNG,
			text_color=MAU_CHU_PHU,
		)
		nhan_trai.pack(anchor="w")

		entry = ctk.CTkEntry(
			khung,
			textvariable=bien,
			border_color=MAU_DUONG_BIEN,
		)
		entry.pack(fill="x", pady=(6, 0))

	def tao_hang_switch(self, cha, nhan, bien):
		khung = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
		khung.pack(fill="x", pady=8)

		nhan_trai = ctk.CTkLabel(
			khung,
			text=nhan,
			font=FONT_NOI_DUNG,
			text_color=MAU_CHU_PHU,
		)
		nhan_trai.pack(side="left")

		cong_tac = ctk.CTkSwitch(
			khung,
			text="",
			variable=bien,
			onvalue=True,
			offvalue=False,
			progress_color=MAU_CHINH,
		)
		cong_tac.pack(side="right")

	def tao_khung_hanh_dong(self, cha):
		khung = ctk.CTkFrame(cha, fg_color=MAU_NEN_SANG, corner_radius=0)
		khung.grid(row=1, column=0, columnspan=2, sticky="ew")
		khung.grid_columnconfigure(0, weight=1)

		self.nhan_trang_thai = ctk.CTkLabel(
			khung,
			text="",
			font=FONT_NOI_DUNG,
			text_color=MAU_CHU_PHU,
		)
		self.nhan_trang_thai.pack(side="left", padx=10)

		nut_luu = ctk.CTkButton(
			khung,
			text="Lưu cấu hình",
			font=FONT_NOI_DUNG_BOLD,
			fg_color=MAU_CHINH,
			hover_color=MAU_CHINH_HOVER,
			command=self.luu_cau_hinh,
			height=42,
		)
		nut_luu.pack(anchor="e", padx=10, pady=10)

	def luu_cau_hinh(self):
		self._settings.api_base_url = self.api_url.get().strip().rstrip("/")
		self._settings.warning_threshold = float(self.nguong_canh_bao.get())
		self._settings.danger_threshold = float(self.nguong_nguy_hiem.get())
		self._settings.humidity_threshold = float(self.nguong_do_am.get())
		self._settings.refresh_ms = int(self.tan_suat_lay_mau.get()) * 1000
		self._settings.sound_alert = bool(self.can_bao_am_thanh.get())
		self._settings.email_alert = bool(self.gui_email.get())

		self._on_save(self._settings)
		self.nhan_trang_thai.configure(text="Đã lưu và đồng bộ cấu hình")

__all__ = ["SettingsView"]