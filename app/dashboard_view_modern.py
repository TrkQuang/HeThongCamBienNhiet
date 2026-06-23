from datetime import datetime
from typing import Optional
import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .data_service import DataService
from .widgets import *

MAU_BIEN_DO = {"NORMAL": MAU_THANH_CONG, "WARNING": MAU_CANH_BAO, "DANGER": MAU_NGUY_HIEM}

# Keep at most this many history row widgets reused
_MAX_HISTORY_ROWS = 5


class ChiBaoTron(tk.Canvas):
    """Vòng tròn hiển thị nhiệt độ — partial update via itemconfigure."""

    def __init__(self, parent, nhiet_do: float, warn: float = 38.0, danger: float = 43.0, **kwargs):
        super().__init__(parent, **kwargs)
        self._warn = warn
        self._danger = danger
        ban_kinh, tam_x, tam_y = 25, 35, 35
        self._bx, self._by = tam_x, tam_y
        self._bk = ban_kinh
        mau = mau_theo_nguong(nhiet_do, warn, danger)
        self._outer = self.create_oval(tam_x - ban_kinh, tam_y - ban_kinh,
                                       tam_x + ban_kinh, tam_y + ban_kinh,
                                       fill="#E0E0E0", outline="#CCCCCC", width=1)
        ban_kinh_trong = ban_kinh * 0.8
        self._inner = self.create_oval(tam_x - ban_kinh_trong, tam_y - ban_kinh_trong,
                                       tam_x + ban_kinh_trong, tam_y + ban_kinh_trong,
                                       fill=mau, outline=mau, width=0)
        self._text = self.create_text(tam_x, tam_y, text=f"{nhiet_do:.0f}°C",
                                      font=("Arial", 10, "bold"), fill="white")

    def update_temp(self, nhiet_do: float, warn: float, danger: float):
        mau = mau_theo_nguong(nhiet_do, warn, danger)
        self.itemconfigure(self._inner, fill=mau, outline=mau)
        self.itemconfigure(self._text, text=f"{nhiet_do:.0f}°C")


class DashboardView(ctk.CTkFrame):
    """Màn hình tổng quan: partial updates, incremental history, FPS limit."""

    def __init__(self, parent, data_service: DataService):
        super().__init__(parent, fg_color=MAU_NEN_SANG)
        self._ds = data_service
        self._thong_bao_hang_doi = []
        self._dang_hien_thong_bao = False
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── previous-state tracking for partial updates ────────────────
        self._prev_temp = ""
        self._prev_humidity = ""
        self._prev_threshold = ""
        self._prev_status = ""
        self._prev_time_str = ""
        self._prev_warn = 0.0
        self._prev_danger = 0.0
        self._prev_refresh_version = -1

        # Reusable history row widgets and ChiBaoTron references
        self._history_rows: list = []
        self._history_bulbs: list = []  # list of ChiBaoTron per row
        self._prev_history_len = -1

        self.tao_giao_dien()
        self._ds.subscribe(lambda: self.after(0, self.cap_nhat_giao_dien))

    # ==================================================
    # Tạo giao diện (one-shot)
    # ==================================================
    def tao_giao_dien(self):
        khung_chinh = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_chinh.grid(row=0, column=0, sticky="nsew")
        khung_chinh.grid_rowconfigure(1, weight=1)
        khung_chinh.grid_columnconfigure(0, weight=1)

        khung_tieu_de = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_tieu_de.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(khung_tieu_de, text="Bảng Điều Khiển", font=FONT_TIEU_DE, text_color=MAU_CHU_CHINH).pack(side="left")
        ctk.CTkButton(khung_tieu_de, text="🔄 Làm mới", width=100,
                       fg_color=MAU_CHINH, hover_color=MAU_CHINH_HOVER,
                       command=self._ds.force_refresh).pack(side="right", padx=20)
        self.nhan_thoi_gian = ctk.CTkLabel(khung_tieu_de, text="", font=FONT_NHAN, text_color=MAU_CHU_PHU)
        self.nhan_thoi_gian.pack(side="right")

        khung_noi_dung = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_noi_dung.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        khung_noi_dung.grid_rowconfigure(1, weight=1)
        khung_noi_dung.grid_columnconfigure(0, weight=1)

        khung_hang_tren = ctk.CTkFrame(khung_noi_dung, fg_color=MAU_NEN_SANG)
        khung_hang_tren.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        khung_hang_tren.grid_rowconfigure(0, weight=1)
        khung_hang_tren.grid_columnconfigure(1, weight=1)

        self.tao_the_trang_thai(khung_hang_tren)
        self.tao_the_bieu_do(khung_hang_tren)
        self.tao_the_lich_su(khung_noi_dung)

    def tao_the_trang_thai(self, cha):
        the = The(cha, width=280, height=280)
        the.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        the.grid_propagate(False)
        khung_trong = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        khung_trong.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(khung_trong, text="Nhiệt độ hiện tại", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_PHU).pack(anchor="w")
        self.nhan_trang_thai = ctk.CTkLabel(khung_trong, text="NORMAL", font=FONT_NOI_DUNG_BOLD, text_color=MAU_THANH_CONG)
        self.nhan_trang_thai.pack(anchor="w", pady=(0, 5))
        self.nhan_nhiet_do = ctk.CTkLabel(khung_trong, text="--°C", font=FONT_SO_LON, text_color=MAU_CHINH)
        self.nhan_nhiet_do.pack(pady=(10, 20))

        self.nut_do_ngay = ctk.CTkButton(khung_trong, text="📡 Đo ngay", font=FONT_NOI_DUNG_BOLD,
                                          fg_color=MAU_CHINH, hover_color=MAU_CHINH_HOVER,
                                          command=self.do_ngay)
        self.nut_do_ngay.pack(pady=(0, 10))
        ctk.CTkFrame(khung_trong, height=1, fg_color=MAU_DUONG_BIEN).pack(fill="x", pady=15)
        self.nhan_do_am = self.tao_hang_thong_tin(khung_trong, "Độ ẩm:", "--%")
        self.nhan_nguong = self.tao_hang_thong_tin(khung_trong, "Ngưỡng:", "--°C")

    def tao_hang_thong_tin(self, cha, nhan, gia_tri):
        khung = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
        khung.pack(fill="x", pady=2)
        ctk.CTkLabel(khung, text=nhan, font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(side="left")
        nhan_gia_tri = ctk.CTkLabel(khung, text=gia_tri, font=FONT_NOI_DUNG_BOLD, text_color=MAU_CHU_CHINH)
        nhan_gia_tri.pack(side="right")
        return nhan_gia_tri

    def tao_the_bieu_do(self, cha):
        the = The(cha)
        the.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(the, text="Xu hướng nhiệt độ", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", padx=25, pady=20)
        khung_canvas = ctk.CTkFrame(the, fg_color=MAU_NEN_SANG)
        khung_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.hinh = Figure(figsize=(6, 3.5), dpi=100, facecolor=MAU_NEN_SANG)
        self.truc_bieu_do = self.hinh.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.hinh, master=khung_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def tao_the_lich_su(self, cha):
        the = The(cha)
        the.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(the, text="Dữ liệu gần đây", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", padx=25, pady=20)
        self.khung_lich_su = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        self.khung_lich_su.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        # Pre-create _MAX_HISTORY_ROWS reusable rows
        self._history_rows = []
        self._history_bulbs = []
        for _ in range(_MAX_HISTORY_ROWS):
            row = ctk.CTkFrame(self.khung_lich_su, fg_color=MAU_THE_BG)
            ts = ctk.CTkLabel(row, text="", font=FONT_NOI_DUNG_BOLD, width=60)
            ts.pack(side="left", padx=10)
            bulb = ChiBaoTron(row, 0, 50, 60, width=70, height=70, bg=MAU_THE_BG, highlightthickness=0)
            bulb.pack(side="left", padx=10)
            temp_lbl = ctk.CTkLabel(row, text="", font=FONT_NOI_DUNG, text_color=MAU_CHU_CHINH)
            temp_lbl.pack(side="left", padx=10)
            bar = ctk.CTkProgressBar(row, fg_color=MAU_DUONG_BIEN, progress_color=MAU_THANH_CONG, height=6)
            bar.pack(side="left", fill="x", expand=True, padx=20)
            self._history_rows.append({"frame": row, "ts": ts, "temp": temp_lbl, "bar": bar})
            self._history_bulbs.append(bulb)
            row.pack(fill="x", pady=5)

    # ==================================================
    # Sự kiện
    # ==================================================
    def do_ngay(self):
        self._ds.request_immediate_measure()
        self.nut_do_ngay.configure(text="⏳ Đang đo...")
        self.after(5000, lambda: self.nut_do_ngay.configure(text="📡 Đo ngay"))
        self.them_thong_bao("Đã gửi yêu cầu đo tới thiết bị", "info")

    def cap_nhat_giao_dien(self):
        self.after(0, self.render)

    # ==================================================
    # Render dữ liệu — partial update only
    # ==================================================
    def render(self):
        if not self._ds.device_id:
            self.nhan_nhiet_do.configure(text="No Device")
            return

        # Detect force_refresh → reset all _prev_* so full re-render happens
        if self._ds._refresh_version != self._prev_refresh_version:
            self._prev_refresh_version = self._ds._refresh_version
            self._prev_temp = ""
            self._prev_warn = 0.0
            self._prev_danger = 0.0
            self._prev_status = ""
            self._prev_threshold = ""

        du_lieu_hien_tai = self._ds.current_data
        if du_lieu_hien_tai:
            nhiet_do_hien_tai = float(du_lieu_hien_tai.get("temp", 0))
            do_am_hien_tai = float(du_lieu_hien_tai.get("humidity", 0))
            trang_thai_canh_bao = self._ds.get_status(nhiet_do_hien_tai, do_am_hien_tai)
            self.cap_nhat_trang_thai(nhiet_do_hien_tai, do_am_hien_tai, trang_thai_canh_bao)

        # Incremental history update
        self.ve_lich_su()

        # Chart — only redraw when history changes
        du_lieu_lich_su = list(reversed(self._ds.history[:10]))
        if du_lieu_lich_su:
            danh_sach_thoi_gian = [self.dinh_dang_thoi_gian(
                muc_du_lieu.get("ts") or muc_du_lieu.get("timestamp")
            ) for muc_du_lieu in du_lieu_lich_su]
            danh_sach_nhiet_do = [float(muc_du_lieu.get("temp", 0)) for muc_du_lieu in du_lieu_lich_su]
            self.ve_bieu_do(danh_sach_thoi_gian, danh_sach_nhiet_do)

        # Time — partial
        ts = datetime.now().strftime("%d/%m/%Y • %H:%M")
        if ts != self._prev_time_str:
            self.nhan_thoi_gian.configure(text=ts)
            self._prev_time_str = ts

    def cap_nhat_trang_thai(self, nhiet_do_hien_tai, do_am_hien_tai, trang_thai_canh_bao):
        warn = self._ds.settings.warning_threshold
        danger = self._ds.settings.danger_threshold
        warn_changed = warn != self._prev_warn
        danger_changed = danger != self._prev_danger

        temp_str = f"{nhiet_do_hien_tai:.1f}°C"
        hum_str = f"{do_am_hien_tai:.0f}%"
        thresh_str = f"{warn:.1f}°C"

        if temp_str != self._prev_temp or warn_changed or danger_changed:
            color = mau_theo_nguong(nhiet_do_hien_tai, warn, danger)
            self.nhan_nhiet_do.configure(text=temp_str, text_color=color)
            self._prev_temp = temp_str
            self._prev_warn = warn
            self._prev_danger = danger
        if hum_str != self._prev_humidity:
            self.nhan_do_am.configure(text=hum_str)
            self._prev_humidity = hum_str
        if thresh_str != self._prev_threshold:
            self.nhan_nguong.configure(text=thresh_str)
            self._prev_threshold = thresh_str
        if trang_thai_canh_bao != self._prev_status or warn_changed or danger_changed:
            self.nhan_trang_thai.configure(
                text=trang_thai_canh_bao,
                text_color=MAU_BIEN_DO.get(trang_thai_canh_bao, MAU_THANH_CONG)
            )
            self._prev_status = trang_thai_canh_bao

    def ve_bieu_do(self, danh_sach_thoi_gian, danh_sach_nhiet_do):
        self.truc_bieu_do.clear()
        self.truc_bieu_do.set_facecolor(MAU_NEN_SANG)
        self.truc_bieu_do.grid(True, alpha=0.2, linestyle="--")
        warn = self._ds.settings.warning_threshold
        danger = self._ds.settings.danger_threshold
        final_color = mau_theo_nguong(danh_sach_nhiet_do[-1], warn, danger) if danh_sach_nhiet_do else MAU_CHINH
        self.truc_bieu_do.plot(danh_sach_thoi_gian, danh_sach_nhiet_do, color=final_color, linewidth=2, alpha=0.7)
        mau_colors = [mau_theo_nguong(t, warn, danger) for t in danh_sach_nhiet_do]
        for i in range(len(danh_sach_thoi_gian)):
            self.truc_bieu_do.scatter(danh_sach_thoi_gian[i], danh_sach_nhiet_do[i], color=mau_colors[i], s=50, zorder=5)
        self.truc_bieu_do.fill_between(range(len(danh_sach_thoi_gian)), danh_sach_nhiet_do, alpha=0.08, color=final_color)
        self.truc_bieu_do.spines["top"].set_visible(False)
        self.truc_bieu_do.spines["right"].set_visible(False)
        self.canvas.draw()

    def ve_lich_su(self):
        """Incremental history: update reusable row widgets in place."""
        history = self._ds.history[:5]
        n = len(history)
        # Show/hide rows based on count
        for idx, row_data in enumerate(self._history_rows):
            frame = row_data["frame"]
            if idx < n:
                frame.pack(fill="x", pady=5)
            else:
                frame.pack_forget()
                continue

            entry = history[idx]
            nhiet_do = float(entry.get("temp", 0))
            warn = self._ds.settings.warning_threshold
            danger = self._ds.settings.danger_threshold
            ts = self.dinh_dang_thoi_gian(entry.get("timestamp") or entry.get("ts"))
            mau = mau_theo_nguong(nhiet_do, warn, danger)

            row_data["ts"].configure(text=ts)
            row_data["temp"].configure(text=f"{nhiet_do:.1f}°C", text_color=mau)
            row_data["bar"].configure(progress_color=mau)
            row_data["bar"].set(min(nhiet_do / 45.0, 1.0))
            # Update bulb in-place
            self._history_bulbs[idx].update_temp(nhiet_do, warn, danger)

        self._prev_history_len = n

    @staticmethod
    def dinh_dang_thoi_gian(thoi_gian_do) -> str:
        if not thoi_gian_do:
            return "--"
        try:
            return datetime.fromisoformat(str(thoi_gian_do).replace("Z", "+00:00")).strftime("%H:%M")
        except Exception:
            return "--"

    # ==================================================
    # Toast thông báo
    # ==================================================
    def them_thong_bao(self, thong_diep, muc_do="info"):
        self._thong_bao_hang_doi.append((thong_diep, muc_do))
        if not self._dang_hien_thong_bao:
            self.hien_thong_bao()

    def hien_thong_bao(self):
        if not self._thong_bao_hang_doi:
            self._dang_hien_thong_bao = False
            return
        self._dang_hien_thong_bao = True
        thong_diep, muc_do = self._thong_bao_hang_doi.pop(0)
        mau_nen = {"error": MAU_NGUY_HIEM, "warning": MAU_CANH_BAO}.get(muc_do, MAU_THANH_CONG)
        hop_thoai = ctk.CTkFrame(self, fg_color=mau_nen, corner_radius=8)
        hop_thoai.place(relx=0.98, rely=0.02, anchor="ne")
        ctk.CTkLabel(hop_thoai, text=thong_diep, text_color="white", font=FONT_NHAN).pack(padx=15, pady=10)
        self.after(3000, lambda: [hop_thoai.destroy(), self.after(200, self.hien_thong_bao)])


__all__ = ["DashboardView"]
