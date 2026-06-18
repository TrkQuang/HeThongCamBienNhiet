from datetime import datetime
import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .data_service import DataService
from .widgets import *

class ChiBaoTron(tk.Canvas):
    def __init__(self, parent, nhiet_do: float, **kwargs):
        super().__init__(parent, **kwargs)
        self.nhiet_do = nhiet_do
        bk, tx, ty = 25, 35, 35
        mau = mau_theo_nhiet_do(nhiet_do)
        self.create_oval(tx - bk, ty - bk, tx + bk, ty + bk, fill="#E0E0E0", outline="#CCCCCC", width=1)
        bkt = bk * 0.8
        self.create_oval(tx - bkt, ty - bkt, tx + bkt, ty + bkt, fill=mau, outline=mau, width=0)
        self.create_text(tx, ty, text=f"{nhiet_do:.0f}°C", font=("Arial", 10, "bold"), fill="white")

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, data_service: DataService):
        super().__init__(parent, fg_color=MAU_NEN_SANG)
        self._ds = data_service
        self._toast_queue, self._toast_showing = [], False
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tao_giao_dien()
        self._ds.subscribe(self.cap_nhat_giao_dien)

    def tao_giao_dien(self):
        kc = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
        kc.grid(row=0, column=0, sticky="nsew")
        kc.grid_rowconfigure(1, weight=1)
        kc.grid_columnconfigure(0, weight=1)

        td = ctk.CTkFrame(kc, fg_color=MAU_NEN_SANG, corner_radius=0)
        td.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(td, text="Bảng Điều Khiển", font=FONT_TIEU_DE, text_color=MAU_CHU_CHINH).pack(side="left")
        ctk.CTkButton(td, text="🔄 Làm mới", width=100, fg_color=MAU_CHINH, hover_color=MAU_CHINH_HOVER, command=self._ds.refresh_all).pack(side="right", padx=20)
        self.nhan_thoi_gian = ctk.CTkLabel(td, text="", font=FONT_NHAN, text_color=MAU_CHU_PHU)
        self.nhan_thoi_gian.pack(side="right")

        nd = ctk.CTkFrame(kc, fg_color=MAU_NEN_SANG, corner_radius=0)
        nd.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        nd.grid_rowconfigure(1, weight=1)
        nd.grid_columnconfigure(0, weight=1)

        tren = ctk.CTkFrame(nd, fg_color=MAU_NEN_SANG)
        tren.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        tren.grid_rowconfigure(0, weight=1)
        tren.grid_columnconfigure(1, weight=1)

        self.tao_the_trang_thai(tren)
        self.tao_the_bieu_do(tren)
        
        the_ls = The(nd)
        the_ls.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(the_ls, text="Dữ liệu gần đây", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", padx=25, pady=20)
        self.khung_lich_su = ctk.CTkFrame(the_ls, fg_color=MAU_THE_BG)
        self.khung_lich_su.pack(fill="both", expand=True, padx=25, pady=(0, 25))

    def tao_the_trang_thai(self, cha):
        the = The(cha, width=280, height=280)
        the.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        the.grid_propagate(False)
        trong = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        trong.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(trong, text="Nhiệt độ hiện tại", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_PHU).pack(anchor="w")
        self.nhan_trang_thai = ctk.CTkLabel(trong, text="NORMAL", font=FONT_NOI_DUNG_BOLD, text_color=MAU_THANH_CONG)
        self.nhan_trang_thai.pack(anchor="w", pady=(0, 5))
        self.nhan_nhiet_do = ctk.CTkLabel(trong, text="--°C", font=FONT_SO_LON, text_color=MAU_CHINH)
        self.nhan_nhiet_do.pack(pady=(10, 20))
        
        self.nut_do = ctk.CTkButton(trong, text="📡 Đo ngay", font=FONT_NOI_DUNG_BOLD, fg_color=MAU_CHINH, hover_color=MAU_CHINH_HOVER, command=self.do_ngay)
        self.nut_do.pack(pady=(0, 10))
        ctk.CTkFrame(trong, height=1, fg_color=MAU_DUONG_BIEN).pack(fill="x", pady=15)
        self.nhan_do_am = self.tao_hang(trong, "Độ ẩm:", "--%")
        self.nhan_nguong = self.tao_hang(trong, "Ngưỡng:", "--°C")

    def tao_hang(self, cha, nhan, gia_tri):
        h = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
        h.pack(fill="x", pady=2)
        ctk.CTkLabel(h, text=nhan, font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(side="left")
        n = ctk.CTkLabel(h, text=gia_tri, font=FONT_NOI_DUNG_BOLD, text_color=MAU_CHU_CHINH)
        n.pack(side="right")
        return n

    def tao_the_bieu_do(self, cha):
        the = The(cha)
        the.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(the, text="Xu hướng nhiệt độ", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", padx=25, pady=20)
        cv = ctk.CTkFrame(the, fg_color=MAU_NEN_SANG)
        cv.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.fig = Figure(figsize=(6, 3.5), dpi=100, facecolor=MAU_NEN_SANG)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=cv)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def do_ngay(self):
        self._ds.request_immediate_measure()
        self.nut_do.configure(text="⏳ Đang đo...")
        self.after(5000, lambda: self.nut_do.configure(text="📡 Đo ngay"))
        self.them_thong_bao("Đã gửi yêu cầu đo tới thiết bị", "info")

    def cap_nhat_giao_dien(self):
        self.after(0, self.render)

    def render(self):
        if not self._ds.device_id:
            self.nhan_nhiet_do.configure(text="No Device")
            return
        if self._ds.current_data:
            dl = self._ds.current_data
            t, h = float(dl.get("temp", 0)), float(dl.get("humidity", 0))
            st = self._ds.get_status(t, h)
            self.nhan_nhiet_do.configure(text=f"{t:.1f}°C", text_color=mau_theo_nhiet_do(t))
            self.nhan_do_am.configure(text=f"{h:.0f}%")
            self.nhan_nguong.configure(text=f"{self._ds.settings.warning_threshold:.1f}°C")
            self.nhan_trang_thai.configure(text=st, text_color={"NORMAL": MAU_THANH_CONG, "WARNING": MAU_CANH_BAO, "DANGER": MAU_NGUY_HIEM}.get(st, MAU_THANH_CONG))
        if self._ds.history:
            ls = list(reversed(self._ds.history[:10]))
            tg = [self.format_ts(i.get("timestamp") or i.get("ts")) for i in ls]
            nd = [float(i.get("temp", 0)) for i in ls]
            self.ax.clear()
            self.ax.set_facecolor(MAU_NEN_SANG)
            self.ax.grid(True, alpha=0.2, linestyle="--")
            self.ax.plot(tg, nd, marker="o", color=MAU_CHINH, linewidth=2)
            self.ax.fill_between(range(len(tg)), nd, alpha=0.1, color=MAU_CHINH)
            self.ax.spines["top"].set_visible(False)
            self.ax.spines["right"].set_visible(False)
            self.canvas.draw()
            
            for w in self.khung_lich_su.winfo_children(): w.destroy()
            for d in self._ds.history[:5]:
                t = float(d.get("temp", 0))
                h = ctk.CTkFrame(self.khung_lich_su, fg_color=MAU_THE_BG)
                h.pack(fill="x", pady=5)
                ctk.CTkLabel(h, text=self.format_ts(d.get("timestamp") or d.get("ts")), font=FONT_NOI_DUNG_BOLD, width=60).pack(side="left", padx=10)
                ChiBaoTron(h, t, width=70, height=70, bg=MAU_THE_BG, highlightthickness=0).pack(side="left", padx=10)
                ctk.CTkLabel(h, text=f"{t:.1f}°C", font=FONT_NOI_DUNG).pack(side="left", padx=10)
                pb = ctk.CTkProgressBar(h, fg_color=MAU_DUONG_BIEN, progress_color=mau_theo_nhiet_do(t), height=6)
                pb.pack(side="left", fill="x", expand=True, padx=20)
                pb.set(min(t / 45.0, 1.0))
        self.nhan_thoi_gian.configure(text=datetime.now().strftime("%d/%m/%Y • %H:%M"))

    @staticmethod
    def format_ts(ts) -> str:
        if not ts: return "--"
        try: return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).strftime("%H:%M")
        except: return "--"

    def them_thong_bao(self, msg: str, lvl: str = "info"):
        self._toast_queue.append((msg, lvl))
        if not self._toast_showing: self.hien_thong_bao()

    def hien_thong_bao(self):
        if not self._toast_queue:
            self._toast_showing = False
            return
        self._toast_showing = True
        msg, lvl = self._toast_queue.pop(0)
        mau = {"error": MAU_NGUY_HIEM, "warning": MAU_CANH_BAO}.get(lvl, MAU_THANH_CONG)
        t = ctk.CTkFrame(self, fg_color=mau, corner_radius=8)
        t.place(relx=0.98, rely=0.02, anchor="ne")
        ctk.CTkLabel(t, text=msg, text_color="white", font=FONT_NHAN).pack(padx=15, pady=10)
        self.after(3000, lambda: [t.destroy(), self.after(200, self.hien_thong_bao)])

__all__ = ["DashboardView"]