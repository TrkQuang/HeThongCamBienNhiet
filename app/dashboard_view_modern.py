"""
Bảng điều khiển hệ thống quản lý nhiệt độ hiện đại
Xây dựng với CustomTkinter và Matplotlib
"""

import threading
from typing import Optional, List, Dict, Any
import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .data_service import DataService
from .widgets import (
    MAU_NEN_SANG,
    MAU_THE_BG,
    MAU_CHINH,
    MAU_CHINH_HOVER,
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
    mau_theo_nhiet_do,
)


class ChiBaoTron(tk.Canvas):
    def __init__(self, parent, gia_tri, gia_tri_max=50, **kwargs):
        super().__init__(parent, **kwargs)
        self.gia_tri = gia_tri
        self.gia_tri_max = gia_tri_max
        self.ve_tron()

    def ve_tron(self):
        ban_kinh = 25
        tam_x = 35
        tam_y = 35
        mau = mau_theo_nhiet_do(self.gia_tri)

        self.create_oval(
            tam_x - ban_kinh,
            tam_y - ban_kinh,
            tam_x + ban_kinh,
            tam_y + ban_kinh,
            fill="#E0E0E0",
            outline="#CCCCCC",
            width=1,
        )

        ban_kinh_trong = ban_kinh * 0.8
        self.create_oval(
            tam_x - ban_kinh_trong,
            tam_y - ban_kinh_trong,
            tam_x + ban_kinh_trong,
            tam_y + ban_kinh_trong,
            fill=mau,
            outline=mau,
            width=0,
        )

        self.create_text(
            tam_x,
            tam_y,
            text=f"{self.gia_tri:.0f}°C",
            font=("Arial", 10, "bold"),
            fill="white",
        )


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, data_service: DataService):
        super().__init__(parent, fg_color=MAU_NEN_SANG)
        self._ds = data_service
        
        self.nhiet_do_hien_tai = 0.0
        self.do_am = 0.0

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tao_noi_dung_chinh()
        
        # Subscribe to centralized data service
        self._ds.subscribe(self.cap_nhat_giao_dien)

    def tao_noi_dung_chinh(self):
        khung_chinh = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_chinh.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        khung_chinh.grid_rowconfigure(0, weight=0)
        khung_chinh.grid_rowconfigure(1, weight=1)
        khung_chinh.grid_columnconfigure(0, weight=1)

        self.tao_tieu_de(khung_chinh)

        khung_noi_dung = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_noi_dung.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        khung_noi_dung.grid_rowconfigure(0, weight=0)
        khung_noi_dung.grid_rowconfigure(1, weight=1)
        khung_noi_dung.grid_columnconfigure(0, weight=1)
        khung_noi_dung.grid_columnconfigure(1, weight=1)

        khung_tren = ctk.CTkFrame(khung_noi_dung, fg_color=MAU_NEN_SANG)
        khung_tren.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 20))
        khung_tren.grid_columnconfigure(0, weight=0)
        khung_tren.grid_columnconfigure(1, weight=1)

        self.tao_the_trang_thai(khung_tren)
        self.tao_the_bieu_do(khung_tren)

        self.tao_the_dong_thoi_gian(khung_noi_dung)

    def tao_tieu_de(self, cha):
        tieu_de = ctk.CTkFrame(cha, fg_color=MAU_NEN_SANG, corner_radius=0)
        tieu_de.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        tieu_de.grid_columnconfigure(0, weight=1)

        nhan_tieu_de = ctk.CTkLabel(
            tieu_de,
            text="Bảng Điều Khiển",
            font=FONT_TIEU_DE,
            text_color=MAU_CHU_CHINH,
        )
        nhan_tieu_de.pack(side="left", anchor="w")

        self.nut_reload = ctk.CTkButton(
            tieu_de,
            text="🔄 Làm mới",
            width=100,
            height=32,
            fg_color=MAU_CHINH,
            hover_color=MAU_CHINH_HOVER,
            command=self._ds.refresh_all
        )
        self.nut_reload.pack(side="right", padx=20)

        self.nhan_thoi_gian_tieude = ctk.CTkLabel(
            tieu_de,
            text=datetime.now().strftime("%d/%m/%Y • %H:%M"),
            font=FONT_NHAN,
            text_color=MAU_CHU_PHU,
        )
        self.nhan_thoi_gian_tieude.pack(side="right", anchor="e")

    def tao_the_trang_thai(self, cha):
        the = The(cha)
        the.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        the.grid_propagate(False)
        the.configure(width=280, height=280)

        trong = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        trong.pack(fill="both", expand=True, padx=25, pady=25)

        nhan_tieu_de = ctk.CTkLabel(
            trong,
            text="Nhiệt độ hiện tại",
            font=FONT_TIEU_DE_THE,
            text_color=MAU_CHU_PHU,
        )
        nhan_tieu_de.pack(anchor="w", pady=(0, 15))

        # Add status label
        self.nhan_trang_thai = ctk.CTkLabel(
            trong,
            text="NORMAL",
            font=FONT_NOI_DUNG_BOLD,
            text_color=MAU_THANH_CONG,
        )
        self.nhan_trang_thai.pack(anchor="w", pady=(0, 5))

        self.nhan_nhiet_do = ctk.CTkLabel(
            trong,
            text="--°C",
            font=FONT_SO_LON,
            text_color=MAU_CHINH,
        )
        self.nhan_nhiet_do.pack(pady=(10, 20))

        duong_ngan = ctk.CTkFrame(trong, height=1, fg_color=MAU_DUONG_BIEN)
        duong_ngan.pack(fill="x", pady=15)

        khung_thong_tin = ctk.CTkFrame(trong, fg_color=MAU_THE_BG)
        khung_thong_tin.pack(fill="x")

        khung_do_am = ctk.CTkFrame(khung_thong_tin, fg_color=MAU_THE_BG)
        khung_do_am.pack(fill="x", pady=5)

        nhan_do_am = ctk.CTkLabel(
            khung_do_am,
            text="Độ ẩm:",
            font=FONT_NOI_DUNG,
            text_color=MAU_CHU_PHU,
        )
        nhan_do_am.pack(side="left")

        self.nhan_gia_tri_do_am = ctk.CTkLabel(
            khung_do_am,
            text="--%",
            font=FONT_NOI_DUNG_BOLD,
            text_color=MAU_CHU_CHINH,
        )
        self.nhan_gia_tri_do_am.pack(side="right")

        khung_nguong = ctk.CTkFrame(khung_thong_tin, fg_color=MAU_THE_BG)
        khung_nguong.pack(fill="x", pady=5)

        nhan_nguong = ctk.CTkLabel(
            khung_nguong,
            text="Ngưỡng cảnh báo:",
            font=FONT_NOI_DUNG,
            text_color=MAU_CHU_PHU,
        )
        nhan_nguong.pack(side="left")

        self.nhan_gia_tri_nguong = ctk.CTkLabel(
            khung_nguong,
            text="--°C",
            font=FONT_NOI_DUNG_BOLD,
            text_color=MAU_CHU_CHINH,
        )
        self.nhan_gia_tri_nguong.pack(side="right")

    def tao_the_bieu_do(self, cha):
        the = The(cha)
        the.grid(row=0, column=1, sticky="nsew")

        khung_tieu_de = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        khung_tieu_de.pack(fill="x", padx=25, pady=20)

        nhan_tieu_de = ctk.CTkLabel(
            khung_tieu_de,
            text="Xu hướng nhiệt độ",
            font=FONT_TIEU_DE_THE,
            text_color=MAU_CHU_CHINH,
        )
        nhan_tieu_de.pack(anchor="w")

        khung_bieu_do = ctk.CTkFrame(the, fg_color=MAU_NEN_SANG)
        khung_bieu_do.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        hinh = Figure(figsize=(6, 3.5), dpi=100, facecolor=MAU_NEN_SANG)
        truc = hinh.add_subplot(111)

        canvas = FigureCanvasTkAgg(hinh, master=khung_bieu_do)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.hinh_bieu_do = hinh
        self.truc_bieu_do = truc
        self.canvas_bieu_do = canvas

    def tao_the_dong_thoi_gian(self, cha):
        the = The(cha)
        the.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(20, 0))

        nhan_tieu_de = ctk.CTkLabel(
            the,
            text="Dữ liệu gần đây",
            font=FONT_TIEU_DE_THE,
            text_color=MAU_CHU_CHINH,
        )
        nhan_tieu_de.pack(anchor="w", padx=25, pady=(20, 20))

        self.khung_dong_thoi_gian = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        self.khung_dong_thoi_gian.pack(fill="both", expand=True, padx=25, pady=(0, 25))

    def cap_nhat_giao_dien(self):
        """Callback from DataService when data changes."""
        self.after(0, self._render_ui)

    def _render_ui(self):
        data = self._ds.current_data
        history = self._ds.history
        settings = self._ds.settings
        
        if not self._ds.device_id:
             self.nhan_nhiet_do.configure(text="No Device")
             return

        # 1. Update Current Stats
        if data:
            temp = float(data.get("temp", 0))
            humidity = float(data.get("humidity", 0))
            
            # Determine status using centralized logic
            current_status = self._ds._determine_status(temp, humidity)
            
            self.nhan_nhiet_do.configure(
                text=f"{temp:.1f}°C",
                text_color=mau_theo_nhiet_do(temp)
            )
            self.nhan_gia_tri_do_am.configure(text=f"{humidity:.0f}%")
            
            # Update status label
            if current_status == "DANGER":
                self.nhan_trang_thai.configure(text="DANGER", text_color=MAU_NGUY_HIEM)
            elif current_status == "WARNING":
                self.nhan_trang_thai.configure(text="WARNING", text_color=MAU_CANH_BAO)
            else:
                self.nhan_trang_thai.configure(text="NORMAL", text_color=MAU_THANH_CONG)
            
            # Update threshold display with status-appropriate color
            threshold = settings.warning_threshold
            if current_status == "DANGER":
                mau_nguong = MAU_NGUY_HIEM
            elif current_status == "WARNING":
                mau_nguong = MAU_CANH_BAO
            else:
                mau_nguong = MAU_CHU_CHINH
                
            self.nhan_gia_tri_nguong.configure(
                text=f"{threshold:.1f}°C",
                text_color=mau_nguong
            )

        # 2. Update Chart
        if history:
            self._cap_nhat_bieu_do(history)
            self._cap_nhat_dong_thoi_gian(history)

        self.nhan_thoi_gian_tieude.configure(text=datetime.now().strftime("%d/%m/%Y • %H:%M"))

    def _dinh_dang_gio(self, raw_ts: Optional[str]) -> str:
        if not raw_ts:
            return "--"
        ts = str(raw_ts).replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(ts)
            return dt.strftime("%H:%M")
        except ValueError:
            return "--"

    def _cap_nhat_bieu_do(self, readings) -> None:
        readings_rev = list(reversed(readings))[:10]
        gio = [self._dinh_dang_gio(item.get("timestamp") or item.get("ts")) for item in readings_rev]
        nhiet_do_list = [float(item.get("temp", 0)) for item in readings_rev]

        self.truc_bieu_do.clear()
        self.truc_bieu_do.set_facecolor(MAU_NEN_SANG)
        self.truc_bieu_do.grid(True, alpha=0.2, linestyle="--")
        
        self.truc_bieu_do.plot(
            gio,
            nhiet_do_list,
            marker="o",
            linewidth=2.5,
            color=MAU_CHINH,
            label="Nhiệt độ"
        )
        self.truc_bieu_do.fill_between(range(len(gio)), nhiet_do_list, alpha=0.1, color=MAU_CHINH)
        
        self.truc_bieu_do.spines["top"].set_visible(False)
        self.truc_bieu_do.spines["right"].set_visible(False)
        self.truc_bieu_do.tick_params(axis="both", labelsize=8)
        
        self.canvas_bieu_do.draw()

    def _cap_nhat_dong_thoi_gian(self, readings) -> None:
        for child in self.khung_dong_thoi_gian.winfo_children():
            child.destroy()

        # Show last 5 readings
        for item in readings[:5]:
            nhiet_do = float(item.get("temp", 0))
            gio = self._dinh_dang_gio(item.get("timestamp") or item.get("ts"))

            muc_thoi_gian = ctk.CTkFrame(self.khung_dong_thoi_gian, fg_color=MAU_THE_BG)
            muc_thoi_gian.pack(fill="x", pady=5)

            nhan_gio = ctk.CTkLabel(muc_thoi_gian, text=gio, font=FONT_NOI_DUNG_BOLD, width=60)
            nhan_gio.pack(side="left", padx=10)

            canvas_chi_bao = ChiBaoTron(muc_thoi_gian, nhiet_do, width=70, height=70, bg=MAU_THE_BG, highlightthickness=0)
            canvas_chi_bao.pack(side="left", padx=10)

            nhan_nhiet_do = ctk.CTkLabel(muc_thoi_gian, text=f"{nhiet_do:.1f}°C", font=FONT_NOI_DUNG)
            nhan_nhiet_do.pack(side="left", padx=10)

            thanh_tien_trinh = ctk.CTkProgressBar(muc_thoi_gian, fg_color=MAU_DUONG_BIEN, progress_color=mau_theo_nhiet_do(nhiet_do), height=6)
            thanh_tien_trinh.pack(side="left", fill="x", expand=True, padx=20)
            thanh_tien_trinh.set(min(nhiet_do / 45.0, 1.0))


__all__ = ["DashboardView"]