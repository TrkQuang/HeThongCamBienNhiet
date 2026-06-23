import customtkinter as ctk
import tkinter as tk
from typing import Callable

from .data_service import DataService
from .settings_store import AppSettings
from .widgets import *


class SettingsView(ctk.CTkFrame):
    """Màn hình cài đặt ngưỡng, API, thông báo."""

    def __init__(self, parent, data_service: DataService, on_save: Callable[[AppSettings], None]):
        super().__init__(parent, fg_color=MAU_NEN_SANG)
        self._on_save = on_save
        self._ds = data_service
        self._cau_hinh = data_service.settings

        self.nguong_canh_bao = tk.DoubleVar(value=self._cau_hinh.warning_threshold)
        self.nguong_nguy_hiem = tk.DoubleVar(value=self._cau_hinh.danger_threshold)
        self.nguong_do_am = tk.DoubleVar(value=self._cau_hinh.humidity_threshold)
        self.tan_suat_lay_mau = tk.IntVar(value=max(int(self._cau_hinh.refresh_ms / 60000), 1))
        self.bat_am_thanh = tk.BooleanVar(value=self._cau_hinh.sound_alert)
        self.gui_email = tk.BooleanVar(value=self._cau_hinh.email_alert)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tao_giao_dien()
        self._ds.subscribe(lambda: self.after(0, self.cap_nhat_giao_dien))

    # ==================================================
    # Tạo giao diện cài đặt hệ thống
    # ==================================================
    def tao_giao_dien(self):
        khung_chinh = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_chinh.grid(row=0, column=0, sticky="nsew")
        khung_chinh.grid_rowconfigure(1, weight=1)
        khung_chinh.grid_columnconfigure(0, weight=1)

        khung_tieu_de = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_tieu_de.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(khung_tieu_de, text="Cài đặt hệ thống", font=FONT_TIEU_DE, text_color=MAU_CHU_CHINH).pack(side="left")

        khung_noi_dung = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_noi_dung.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        khung_noi_dung.grid_rowconfigure(0, weight=1)
        khung_noi_dung.grid_columnconfigure((0, 1), weight=1)

        self.tao_the_nguong(khung_noi_dung)
        self.tao_the_ket_noi(khung_noi_dung)
        self.tao_hang_luu(khung_noi_dung)

    def tao_hang_luu(self, cha):
        khung_luu = ctk.CTkFrame(cha, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_luu.grid(row=1, column=0, columnspan=2, sticky="ew")
        khung_luu.grid_columnconfigure(0, weight=1)
        self.nhan_trang_thai_luu = ctk.CTkLabel(khung_luu, text="", font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU)
        self.nhan_trang_thai_luu.pack(side="left", padx=10)
        ctk.CTkButton(
            khung_luu,
            text="Lưu cấu hình",
            font=FONT_NOI_DUNG_BOLD,
            fg_color=MAU_CHINH,
            hover_color=MAU_CHINH_HOVER,
            command=self.luu,
            height=42,
        ).pack(anchor="e", padx=10, pady=10)

    def tao_the_nguong(self, cha):
        the = The(cha)
        the.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=(0, 15))
        khung = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        khung.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(khung, text="Cấu hình ngưỡng", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", pady=(0, 15))

        danh_sach_nguong = [
            ("Ngưỡng cảnh báo (°C)", self.nguong_canh_bao, 20, 45),
            ("Ngưỡng nguy hiểm (°C)", self.nguong_nguy_hiem, 30, 55),
            ("Ngưỡng độ ẩm (%)", self.nguong_do_am, 40, 100),
        ]
        for ten_nguong, bien_nguong, gia_tri_nho_nhat, gia_tri_lon_nhat in danh_sach_nguong:
            self.tao_slider(khung, ten_nguong, bien_nguong, gia_tri_nho_nhat, gia_tri_lon_nhat)

        khung_tan_suat = ctk.CTkFrame(khung, fg_color=MAU_THE_BG)
        khung_tan_suat.pack(fill="x", pady=10)
        ctk.CTkLabel(khung_tan_suat, text="Tần suất lấy mẫu (Phút)", font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(anchor="w")
        ctk.CTkComboBox(
            khung_tan_suat,
            values=["1", "5", "10", "15", "30"],
            variable=self.tan_suat_lay_mau,
            state="readonly",
            command=lambda gia_tri: self.tan_suat_lay_mau.set(int(gia_tri)),
        ).pack(fill="x", pady=(6, 0))

    def tao_slider(self, cha, ten_nguong, bien_nguong, gia_tri_nho_nhat, gia_tri_lon_nhat):
        khung_slider = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
        khung_slider.pack(fill="x", pady=10)
        ctk.CTkLabel(khung_slider, text=ten_nguong, font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(anchor="w")

        khung_gia_tri = ctk.CTkFrame(khung_slider, fg_color=MAU_THE_BG)
        khung_gia_tri.pack(fill="x", pady=(6, 0))
        nhan_gia_tri = ctk.CTkLabel(
            khung_gia_tri,
            text=str(round(bien_nguong.get(), 1)),
            font=FONT_NOI_DUNG_BOLD,
            text_color=MAU_CHU_CHINH,
            width=60,
        )
        thanh_truot = ctk.CTkSlider(
            khung_gia_tri,
            from_=gia_tri_nho_nhat,
            to=gia_tri_lon_nhat,
            command=lambda gia_tri: self.cap_nhat_slider(bien_nguong, nhan_gia_tri, gia_tri),
        )
        thanh_truot.pack(side="left", fill="x", expand=True, padx=(0, 10))
        thanh_truot.set(bien_nguong.get())
        nhan_gia_tri.pack(side="right")

    @staticmethod
    def cap_nhat_slider(bien_nguong, nhan_gia_tri, gia_tri):
        gia_tri_lam_tron = round(gia_tri, 1)
        bien_nguong.set(gia_tri_lam_tron)
        nhan_gia_tri.configure(text=str(gia_tri_lam_tron))

    def tao_the_ket_noi(self, cha):
        the = The(cha)
        the.grid(row=0, column=1, sticky="nsew", pady=(0, 15))
        khung = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        khung.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(khung, text="Kết nối và thông báo", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", pady=(0, 15))

        ctk.CTkFrame(khung, height=1, fg_color=MAU_DUONG_BIEN).pack(fill="x", pady=15)
        for ten_cai_dat, bien_cai_dat in [("Bật cảnh báo âm thanh", self.bat_am_thanh), ("Gửi email khi nguy hiểm", self.gui_email)]:
            khung_switch = ctk.CTkFrame(khung, fg_color=MAU_THE_BG)
            khung_switch.pack(fill="x", pady=8)
            ctk.CTkLabel(khung_switch, text=ten_cai_dat, font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(side="left")
            ctk.CTkSwitch(khung_switch, text="", variable=bien_cai_dat, progress_color=MAU_CHINH).pack(side="right")

    # ==================================================
    # Lưu ngưỡng cảnh báo và cấu hình vào bộ nhớ/app service
    # ==================================================
    def luu(self):
        self._cau_hinh.warning_threshold = float(self.nguong_canh_bao.get())
        self._cau_hinh.danger_threshold = float(self.nguong_nguy_hiem.get())
        self._cau_hinh.humidity_threshold = float(self.nguong_do_am.get())
        self._cau_hinh.refresh_ms = int(self.tan_suat_lay_mau.get()) * 60000
        self._cau_hinh.sound_alert = bool(self.bat_am_thanh.get())
        self._cau_hinh.email_alert = bool(self.gui_email.get())
        self._on_save(self._cau_hinh)
        self.nhan_trang_thai_luu.configure(text="Đã lưu và đồng bộ cấu hình")

    def cap_nhat_giao_dien(self):
        self._cau_hinh = self._ds.settings
        self.nguong_canh_bao.set(self._cau_hinh.warning_threshold)
        self.nguong_nguy_hiem.set(self._cau_hinh.danger_threshold)
        self.nguong_do_am.set(self._cau_hinh.humidity_threshold)
        self.tan_suat_lay_mau.set(max(int(self._cau_hinh.refresh_ms / 60000), 1))
        self.bat_am_thanh.set(self._cau_hinh.sound_alert)
        self.gui_email.set(self._cau_hinh.email_alert)


__all__ = ["SettingsView"]