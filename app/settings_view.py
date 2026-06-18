import customtkinter as ctk
import tkinter as tk
from typing import Callable
from .data_service import DataService
from .settings_store import AppSettings
from .widgets import *

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, data_service: DataService, on_save: Callable[[AppSettings], None]):
        super().__init__(parent, fg_color=MAU_NEN_SANG)
        self._on_save = on_save
        self._ds = data_service
        self._set = data_service.settings
        self.ng_cb = tk.DoubleVar(value=self._set.warning_threshold)
        self.ng_nh = tk.DoubleVar(value=self._set.danger_threshold)
        self.ng_da = tk.DoubleVar(value=self._set.humidity_threshold)
        self.ts = tk.IntVar(value=max(int(self._set.refresh_ms / 60000), 1))
        self.api = tk.StringVar(value=self._set.api_base_url)
        self.cb_am = tk.BooleanVar(value=self._set.sound_alert)
        self.cb_em = tk.BooleanVar(value=self._set.email_alert)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tao_noi_dung()
        self._ds.subscribe(self.cap_nhat_giao_dien)

    def tao_noi_dung(self):
        kc = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
        kc.grid(row=0, column=0, sticky="nsew")
        kc.grid_rowconfigure(1, weight=1)
        kc.grid_columnconfigure(0, weight=1)
        td = ctk.CTkFrame(kc, fg_color=MAU_NEN_SANG, corner_radius=0)
        td.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(td, text="Cài đặt hệ thống", font=FONT_TIEU_DE, text_color=MAU_CHU_CHINH).pack(side="left")
        kn = ctk.CTkFrame(kc, fg_color=MAU_NEN_SANG, corner_radius=0)
        kn.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        kn.grid_rowconfigure(0, weight=1)
        kn.grid_columnconfigure((0, 1), weight=1)
        self.tao_the_nd(kn)
        self.tao_the_kn(kn)
        hd = ctk.CTkFrame(kn, fg_color=MAU_NEN_SANG, corner_radius=0)
        hd.grid(row=1, column=0, columnspan=2, sticky="ew")
        hd.grid_columnconfigure(0, weight=1)
        self.l_st = ctk.CTkLabel(hd, text="", font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU)
        self.l_st.pack(side="left", padx=10)
        ctk.CTkButton(hd, text="Lưu cấu hình", font=FONT_NOI_DUNG_BOLD, fg_color=MAU_CHINH, hover_color=MAU_CHINH_HOVER, command=self.luu, height=42).pack(anchor="e", padx=10, pady=10)

    def tao_the_nd(self, cha):
        the = The(cha)
        the.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=(0, 15))
        k = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        k.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(k, text="Cấu hình ngưỡng", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", pady=(0, 15))
        self.tao_sld(k, "Ngưỡng cảnh báo (°C)", self.ng_cb, 20, 45)
        self.tao_sld(k, "Ngưỡng nguy hiểm (°C)", self.ng_nh, 30, 55)
        self.tao_sld(k, "Ngưỡng độ ẩm (%)", self.ng_da, 40, 100)
        t = ctk.CTkFrame(k, fg_color=MAU_THE_BG)
        t.pack(fill="x", pady=10)
        ctk.CTkLabel(t, text="Tần suất lấy mẫu (Phút)", font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(anchor="w")
        ctk.CTkComboBox(t, values=["1", "5", "10", "15", "30"], variable=self.ts, state="readonly", command=lambda v: self.ts.set(int(v))).pack(fill="x", pady=(6, 0))

    def tao_sld(self, cha, nhan, var, min_v, max_v):
        k = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
        k.pack(fill="x", pady=10)
        ctk.CTkLabel(k, text=nhan, font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(anchor="w")
        kg = ctk.CTkFrame(k, fg_color=MAU_THE_BG)
        kg.pack(fill="x", pady=(6, 0))
        l_v = ctk.CTkLabel(kg, text=str(round(var.get(), 1)), font=FONT_NOI_DUNG_BOLD, text_color=MAU_CHU_CHINH, width=60)
        sl = ctk.CTkSlider(kg, from_=min_v, to=max_v, command=lambda v: [var.set(round(v, 1)), l_v.configure(text=str(round(v, 1)))])
        sl.pack(side="left", fill="x", expand=True, padx=(0, 10))
        sl.set(var.get())
        l_v.pack(side="right")

    def tao_the_kn(self, cha):
        the = The(cha)
        the.grid(row=0, column=1, sticky="nsew", pady=(0, 15))
        k = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        k.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(k, text="Kết nối và thông báo", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", pady=(0, 15))
        h = ctk.CTkFrame(k, fg_color=MAU_THE_BG)
        h.pack(fill="x", pady=10)
        ctk.CTkLabel(h, text="API URL", font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(anchor="w")
        ctk.CTkEntry(h, textvariable=self.api, border_color=MAU_DUONG_BIEN).pack(fill="x", pady=(6, 0))
        ctk.CTkFrame(k, height=1, fg_color=MAU_DUONG_BIEN).pack(fill="x", pady=15)
        for text, var in [("Bật cảnh báo âm thanh", self.cb_am), ("Gửi email khi nguy hiểm", self.cb_em)]:
            h2 = ctk.CTkFrame(k, fg_color=MAU_THE_BG)
            h2.pack(fill="x", pady=8)
            ctk.CTkLabel(h2, text=text, font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(side="left")
            ctk.CTkSwitch(h2, text="", variable=var, progress_color=MAU_CHINH).pack(side="right")

    def luu(self):
        self._set.api_base_url = self.api.get().strip().rstrip("/")
        self._set.warning_threshold = float(self.ng_cb.get())
        self._set.danger_threshold = float(self.ng_nh.get())
        self._set.humidity_threshold = float(self.ng_da.get())
        self._set.refresh_ms = int(self.ts.get()) * 60000
        self._set.sound_alert = bool(self.cb_am.get())
        self._set.email_alert = bool(self.cb_em.get())
        self._on_save(self._set)
        self.l_st.configure(text="Đã lưu và đồng bộ cấu hình")

    def cap_nhat_giao_dien(self):
        self.after(0, self._render)

    def _render(self):
        self._set = self._ds.settings
        self.ng_cb.set(self._set.warning_threshold)
        self.ng_nh.set(self._set.danger_threshold)
        self.ng_da.set(self._set.humidity_threshold)
        self.ts.set(max(int(self._set.refresh_ms / 60000), 1))
        self.api.set(self._set.api_base_url)
        self.cb_am.set(self._set.sound_alert)
        self.cb_em.set(self._set.email_alert)

__all__ = ["SettingsView"]