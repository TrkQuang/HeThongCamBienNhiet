"""
Cua so chinh va dieu huong giao dien
"""

import customtkinter as ctk

from .alert_panel import AlertView
from .dashboard_view_modern import DashboardView
from .settings_view import SettingsView
from .api_client import ApiClient
from .settings_store import AppSettings, load_settings, save_settings
from .widgets import (
	MAU_NEN_SANG,
	MAU_THANH_BEN,
	MAU_CHINH,
	MAU_CHINH_HOVER,
	MAU_CHU_PHU,
	MAU_DUONG_BIEN,
	ap_dung_giao_dien,
)


class MainWindow(ctk.CTk):
	def __init__(self):
		super().__init__()
		ap_dung_giao_dien()

		self._settings = load_settings()
		self._api_client = ApiClient(self._settings.api_base_url)

		self.title("Hệ Thống Quản Lý Nhiệt Độ")
		self.geometry("1400x800")
		self.minsize(1100, 720)

		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=0)
		self.grid_columnconfigure(1, weight=1)

		self._nav_buttons = {}
		self._views = {}

		self.tao_thanh_ben()
		self.tao_noi_dung()
		self.hien_thi_view("Dashboard")

	def tao_thanh_ben(self):
		thanh_ben = ctk.CTkFrame(self, fg_color=MAU_THANH_BEN, corner_radius=0)
		thanh_ben.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
		thanh_ben.grid_propagate(False)
		thanh_ben.configure(width=220)

		tieu_de = ctk.CTkLabel(
			thanh_ben,
			text="HỆ THỐNG\nQUẢN LÝ\nNHIỆT ĐỘ",
			font=("Arial", 16, "bold"),
			text_color=MAU_CHINH,
			justify="center",
		)
		tieu_de.pack(pady=30, padx=20)

		duong_ngan = ctk.CTkFrame(thanh_ben, height=1, fg_color=MAU_DUONG_BIEN)
		duong_ngan.pack(fill="x", padx=20, pady=10)

		cac_muc = [
			("Dashboard", "📊"),
			("Alerts", "🔔"),
			("Settings", "⚙️"),
		]

		for chi_so, (nhan, bieu_tuong) in enumerate(cac_muc):
			nut = ctk.CTkButton(
				thanh_ben,
				text=f"  {bieu_tuong} {nhan}",
				font=("Arial", 12),
				fg_color="transparent" if chi_so > 0 else MAU_CHINH,
				text_color=MAU_CHINH if chi_so > 0 else "white",
				hover_color=MAU_CHINH_HOVER if chi_so == 0 else MAU_CHINH,
				border_width=0,
				corner_radius=8,
				height=40,
				command=lambda l=nhan: self.hien_thi_view(l),
			)
			nut.pack(fill="x", padx=15, pady=8)
			self._nav_buttons[nhan] = nut

		khung_chan = ctk.CTkFrame(thanh_ben, fg_color="transparent")
		khung_chan.pack(side="bottom", fill="x", padx=20, pady=20)

		nhan_chan = ctk.CTkLabel(
			khung_chan,
			text="v1.0 | 2026",
			font=("Arial", 10),
			text_color=MAU_CHU_PHU,
		)
		nhan_chan.pack()

	def tao_noi_dung(self):
		khung_chinh = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
		khung_chinh.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
		khung_chinh.grid_rowconfigure(0, weight=1)
		khung_chinh.grid_columnconfigure(0, weight=1)

		self._views = {
			"Dashboard": DashboardView(khung_chinh, self._api_client, self._settings),
			"Alerts": AlertView(khung_chinh, self._api_client, self._settings),
			"Settings": SettingsView(khung_chinh, self._settings, self._luu_cau_hinh),
		}

		for view in self._views.values():
			view.grid(row=0, column=0, sticky="nsew")

	def hien_thi_view(self, nhan):
		view = self._views.get(nhan)
		if not view:
			return

		view.tkraise()
		for ten, nut in self._nav_buttons.items():
			if ten == nhan:
				nut.configure(fg_color=MAU_CHINH, text_color="white", hover_color=MAU_CHINH_HOVER)
			else:
				nut.configure(fg_color="transparent", text_color=MAU_CHINH, hover_color=MAU_CHINH)

	def _luu_cau_hinh(self, cau_hinh: AppSettings) -> None:
		self._settings = cau_hinh
		save_settings(cau_hinh)
		self._api_client.update_base_url(cau_hinh.api_base_url)

		dashboard = self._views.get("Dashboard")
		if dashboard:
			dashboard.cap_nhat_cau_hinh(cau_hinh)

		alerts = self._views.get("Alerts")
		if alerts:
			alerts.cap_nhat_cau_hinh(cau_hinh)


__all__ = ["MainWindow"]
