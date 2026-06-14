"""
Cua so chinh va dieu huong giao dien - Da Thiet Bi (Multi-Device)
"""

import customtkinter as ctk
import threading
from typing import Dict, Any

from .alert_panel import AlertView
from .dashboard_view_modern import DashboardView
from .settings_view import SettingsView
from .api_client import ApiClient
from .data_service import DataService
from .settings_store import AppSettings, load_settings, save_settings
from .widgets import (
	MAU_NEN_SANG,
	MAU_THANH_BEN,
	MAU_CHINH,
	MAU_CHINH_HOVER,
	MAU_CHU_CHINH,
	MAU_CHU_PHU,
	MAU_DUONG_BIEN,
	MAU_NGUY_HIEM,
	MAU_THE_BG,
	ap_dung_giao_dien,
)

class AddDeviceDialog(ctk.CTkToplevel):
	def __init__(self, master, api_client: ApiClient, on_success):
		super().__init__(master)
		self.title("Thêm Thiết Bị Mới")
		self.geometry("400x300")
		self.attributes("-topmost", True)
		self.resizable(False, False)

		self._api_client = api_client
		self._on_success = on_success

		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		khung = ctk.CTkFrame(self, fg_color=MAU_THE_BG)
		khung.pack(fill="both", expand=True, padx=20, pady=20)

		nhan_tieu_de = ctk.CTkLabel(khung, text="Thêm Thiết Bị", font=("Arial", 16, "bold"), text_color=MAU_CHU_CHINH)
		nhan_tieu_de.pack(pady=(10, 20))

		self.entry_id = ctk.CTkEntry(khung, placeholder_text="Device ID (VD: THM-2026-0001)", width=300)
		self.entry_id.pack(pady=10)

		self.entry_name = ctk.CTkEntry(khung, placeholder_text="Tên hiển thị (Tùy chọn)", width=300)
		self.entry_name.pack(pady=10)

		self.nhan_loi = ctk.CTkLabel(khung, text="", text_color=MAU_NGUY_HIEM)
		self.nhan_loi.pack(pady=5)

		nut_them = ctk.CTkButton(khung, text="Xác nhận", fg_color=MAU_CHINH, hover_color=MAU_CHINH_HOVER, command=self.kiem_tra_them)
		nut_them.pack(pady=(10, 0))

	def kiem_tra_them(self):
		dev_id = self.entry_id.get().strip()
		dev_name = self.entry_name.get().strip() or "Thiết bị mới"

		if not dev_id:
			self.nhan_loi.configure(text="Vui lòng nhập Device ID")
			return

		self.nhan_loi.configure(text="Đang xác minh...", text_color=MAU_CHU_PHU)
		
		def run():
			error = None
			try:
				resp = self._api_client.get_device(dev_id)
				# Based on firebase/device_repo.py, it returns {"exists": True, "device_id": ...}
				if not resp.get("exists", False):
					error = "Không tìm thấy thiết bị trên hệ thống"
			except Exception as e:
				print(f"Verify error: {e}")
				error = "Lỗi kết nối tới máy chủ"
			self.after(0, lambda: h(error))

		def h(error):
			if error:
				self.nhan_loi.configure(text=error, text_color=MAU_NGUY_HIEM)
			else:
				self._on_success(dev_id, dev_name)
				self.destroy()

		threading.Thread(target=run, daemon=True).start()

class MainWindow(ctk.CTk):
	def __init__(self):
		super().__init__()
		ap_dung_giao_dien()

		self._settings = load_settings()
		self._api_client = ApiClient(self._settings.api_base_url)
		# Initialize Centralized Data Service
		self._data_service = DataService(self._api_client, self._settings)

		self.title("Hệ Thống Giám Sát Nhiệt Độ")
		self.geometry("1400x800")
		self.minsize(1100, 720)

		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=0)
		self.grid_columnconfigure(1, weight=1)

		self._device_buttons = {}
		self._current_tab = "Dashboard"

		self.thanh_ben = ctk.CTkFrame(self, fg_color=MAU_THANH_BEN, corner_radius=0)
		self.thanh_ben.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
		
		self.khung_chinh = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
		self.khung_chinh.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

		self.tao_thanh_ben()
		self.tao_noi_dung_chinh()
		
		if self._settings.device_id:
			self.chon_thiet_bi(self._settings.device_id)
		elif self._settings.devices:
			self.chon_thiet_bi(self._settings.devices[0]["id"])
		else:
			self.lam_moi_giao_dien_trong()

	def tao_thanh_ben(self):
		for widget in self.thanh_ben.winfo_children():
			widget.destroy()

		self.thanh_ben.grid_propagate(False)
		self.thanh_ben.configure(width=250)

		khung_tieu_de = ctk.CTkFrame(self.thanh_ben, fg_color="transparent")
		khung_tieu_de.pack(fill="x", pady=20, padx=20)

		nhan_icon = ctk.CTkLabel(khung_tieu_de, text="📡", font=("Arial", 24))
		nhan_icon.pack(side="left")
		
		nhan_tieu_de = ctk.CTkLabel(khung_tieu_de, text="THIẾT BỊ", font=("Arial", 16, "bold"), text_color=MAU_CHINH)
		nhan_tieu_de.pack(side="left", padx=10)

		duong_ngan = ctk.CTkFrame(self.thanh_ben, height=1, fg_color=MAU_DUONG_BIEN)
		duong_ngan.pack(fill="x", padx=20, pady=(0, 10))

		self.khung_danh_sach = ctk.CTkScrollableFrame(self.thanh_ben, fg_color="transparent", bg_color="transparent")
		self.khung_danh_sach.pack(fill="both", expand=True, padx=10)

		nut_them = ctk.CTkButton(
			self.thanh_ben,
			text="+ Thêm thiết bị",
			font=("Arial", 14, "bold"),
			fg_color="transparent",
			border_width=2,
			border_color=MAU_CHINH,
			text_color=MAU_CHINH,
			hover_color=MAU_NEN_SANG,
			height=40,
			command=self.hien_thi_them_thiet_bi,
		)
		nut_them.pack(fill="x", padx=20, pady=20)

		self.render_danh_sach_thiet_bi()

	def render_danh_sach_thiet_bi(self):
		for widget in self.khung_danh_sach.winfo_children():
			widget.destroy()
		self._device_buttons.clear()

		if not self._settings.devices:
			nhan = ctk.CTkLabel(self.khung_danh_sach, text="Chưa có thiết bị nào", text_color=MAU_CHU_PHU)
			nhan.pack(pady=20)
			return

		for dev in self._settings.devices:
			dev_id = dev["id"]
			dev_name = dev.get("name", dev_id)

			nut = ctk.CTkButton(
				self.khung_danh_sach,
				text=f"🏠 {dev_name}\n{dev_id}",
				font=("Arial", 12),
				fg_color="transparent",
				text_color=MAU_CHU_CHINH,
				hover_color=MAU_CHINH_HOVER,
				anchor="w",
				height=50,
				corner_radius=8,
				command=lambda d=dev_id: self.chon_thiet_bi(d)
			)
			nut.pack(fill="x", pady=5)
			self._device_buttons[dev_id] = nut

		self._cap_nhat_mau_nut()

	def _cap_nhat_mau_nut(self):
		for dev_id, nut in self._device_buttons.items():
			if dev_id == self._settings.device_id:
				nut.configure(fg_color=MAU_CHINH, text_color="white", hover_color=MAU_CHINH)
			else:
				nut.configure(fg_color="transparent", text_color=MAU_CHU_CHINH, hover_color=MAU_NEN_SANG)

	def hien_thi_them_thiet_bi(self):
		AddDeviceDialog(self, self._api_client, self.xu_ly_them_thiet_bi)

	def xu_ly_them_thiet_bi(self, dev_id, dev_name):
		# Kiem tra da co chua
		exists = False
		for d in self._settings.devices:
			if d["id"] == dev_id:
				exists = True
				break
		
		if not exists:
			self._settings.devices.append({"id": dev_id, "name": dev_name})
		
		self._settings.device_id = dev_id
		save_settings(self._settings)
		self.render_danh_sach_thiet_bi()
		self.chon_thiet_bi(dev_id)

	def tao_noi_dung_chinh(self):
		self.khung_chinh.grid_rowconfigure(0, weight=0)
		self.khung_chinh.grid_rowconfigure(1, weight=1)
		self.khung_chinh.grid_columnconfigure(0, weight=1)

		khung_tabs = ctk.CTkFrame(self.khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0, height=50)
		khung_tabs.grid(row=0, column=0, sticky="ew")
		khung_tabs.grid_propagate(False)

		self.tab_dashboard = ctk.CTkButton(khung_tabs, text="Tổng quan", fg_color=MAU_CHINH, command=lambda: self.chuyen_tab("Dashboard"))
		self.tab_dashboard.pack(side="left", padx=(20, 10), pady=10)

		self.tab_alerts = ctk.CTkButton(khung_tabs, text="Cảnh báo", fg_color="transparent", text_color=MAU_CHU_CHINH, border_width=1, border_color=MAU_DUONG_BIEN, command=lambda: self.chuyen_tab("Alerts"))
		self.tab_alerts.pack(side="left", padx=10, pady=10)

		self.tab_settings = ctk.CTkButton(khung_tabs, text="Cài đặt", fg_color="transparent", text_color=MAU_CHU_CHINH, border_width=1, border_color=MAU_DUONG_BIEN, command=lambda: self.chuyen_tab("Settings"))
		self.tab_settings.pack(side="left", padx=10, pady=10)

		self.khung_view = ctk.CTkFrame(self.khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
		self.khung_view.grid(row=1, column=0, sticky="nsew")
		self.khung_view.grid_rowconfigure(0, weight=1)
		self.khung_view.grid_columnconfigure(0, weight=1)

		self._views = {
			"Dashboard": DashboardView(self.khung_view, self._data_service),
			"Alerts": AlertView(self.khung_view, self._data_service),
			"Settings": SettingsView(self.khung_view, self._data_service, self._luu_cau_hinh),
		}

		for view in self._views.values():
			view.grid(row=0, column=0, sticky="nsew")

	def chuyen_tab(self, tab_name):
		self._current_tab = tab_name
		for ten, view in self._views.items():
			if ten == tab_name:
				view.tkraise()
		
		# Doi mau tab
		tabs = {
			"Dashboard": self.tab_dashboard,
			"Alerts": self.tab_alerts,
			"Settings": self.tab_settings
		}
		for ten, btn in tabs.items():
			if ten == tab_name:
				btn.configure(fg_color=MAU_CHINH, text_color="white", border_width=0)
			else:
				btn.configure(fg_color="transparent", text_color=MAU_CHU_CHINH, border_width=1, border_color=MAU_DUONG_BIEN)

	def chon_thiet_bi(self, device_id: str):
		self._settings.device_id = device_id
		save_settings(self._settings)
		self._cap_nhat_mau_nut()
		
		# Notify data service about device change
		self._data_service.update_settings(self._settings)
		
		self.chuyen_tab(self._current_tab)

	def lam_moi_giao_dien_trong(self):
		for view in self._views.values():
			view.grid_forget()
		nhan_trong = ctk.CTkLabel(self.khung_view, text="Vui lòng thêm hoặc chọn thiết bị bên trái", font=("Arial", 16), text_color=MAU_CHU_PHU)
		nhan_trong.place(relx=0.5, rely=0.5, anchor="center")

	def _luu_cau_hinh(self, cau_hinh: AppSettings) -> None:
		self._settings = cau_hinh
		save_settings(cau_hinh)
		
		# Sync settings to backend
		def dong_bo_api():
			if cau_hinh.device_id:
				try:
					payload = {
						"temperatureThreshold": cau_hinh.warning_threshold,
						"humidityThreshold": cau_hinh.humidity_threshold,
						"samplingInterval": max(int(cau_hinh.refresh_ms / 60000), 1),
						"notificationEnabled": cau_hinh.sound_alert
					}
					self._api_client.update_settings(cau_hinh.device_id, payload)
				except Exception as e:
					print(f"API sync error: {e}")

		threading.Thread(target=dong_bo_api, daemon=True).start()
		
		# Update data service with new settings (thresholds, API URL, etc)
		self._data_service.update_settings(cau_hinh)


__all__ = ["MainWindow"]