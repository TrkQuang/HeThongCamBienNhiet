import customtkinter as ctk
from datetime import datetime
from .data_service import DataService
from .widgets import *


BANG_TRANG_THAI = {
    "NORMAL": "Bình thường",
    "WARNING": "Vượt ngưỡng",
    "DANGER": "Nguy hiểm!",
}
BANG_NGUY_CO = {
    "NORMAL": "Không có nguy cơ",
    "WARNING": "Nguy cơ cao",
    "DANGER": "Nguy cơ cao",
}


class AlertView(ctk.CTkFrame):
    def __init__(self, parent, data_service: DataService):
        super().__init__(parent, fg_color=MAU_NEN_SANG)
        self._ds = data_service
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tao_noi_dung()
        self._ds.subscribe(self.cap_nhat_giao_dien)

    def tao_noi_dung(self):
        khung = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung.grid(row=0, column=0, sticky="nsew")
        khung.grid_rowconfigure(1, weight=1)
        khung.grid_columnconfigure(0, weight=1)

        td = ctk.CTkFrame(khung, fg_color=MAU_NEN_SANG, corner_radius=0)
        td.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(td, text="Cảnh Báo", font=FONT_TIEU_DE, text_color=MAU_CHU_CHINH).pack(side="left")
        self.nhan_thoi_gian = ctk.CTkLabel(td, text="", font=FONT_NHAN, text_color=MAU_CHU_PHU)
        self.nhan_thoi_gian.pack(side="right")

        nd = ctk.CTkFrame(khung, fg_color=MAU_NEN_SANG, corner_radius=0)
        nd.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        nd.grid_rowconfigure(1, weight=1)
        nd.grid_columnconfigure(0, weight=1)

        tren = ctk.CTkFrame(nd, fg_color=MAU_NEN_SANG)
        tren.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        tren.grid_columnconfigure(0, weight=2)
        tren.grid_columnconfigure(1, weight=1)
        self.tao_the_trang_thai(tren)
        self.tao_cot_goi_y(tren)
        self.tao_the_lich_su(nd)

    def tao_the_trang_thai(self, cha):
        the = The(cha)
        the.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        trong = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        trong.pack(fill="both", expand=True, padx=25, pady=25)
        ctk.CTkLabel(trong, text="Tình trạng hiện tại", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_PHU).pack(anchor="w", pady=(0, 10))
        self.nhan_nhiet_do = ctk.CTkLabel(trong, text="--°C", font=FONT_SO_LON, text_color=MAU_CHINH)
        self.nhan_nhiet_do.pack(anchor="w", pady=(0, 10))
        hang = ctk.CTkFrame(trong, fg_color=MAU_THE_BG)
        hang.pack(fill="x", pady=(0, 10))
        self.nhan_ghi_chu = ctk.CTkLabel(hang, text="Đang chờ...", font=FONT_NOI_DUNG, text_color=MAU_CHU_CHINH)
        self.nhan_ghi_chu.pack(side="left")
        self.huy_hieu = HuyHieu(hang, text="NORMAL", mau=MAU_THANH_CONG)
        self.huy_hieu.pack(side="right")
        ctk.CTkFrame(trong, height=1, fg_color=MAU_DUONG_BIEN).pack(fill="x", pady=15)
        self.nhan_cam_bien = self.tao_hang(trong, "Cảm biến:", "--")
        self.nhan_do_am = self.tao_hang(trong, "Độ ẩm:", "--%")
        self.nhan_nguong = self.tao_hang(trong, "Ngưỡng:", "--°C", MAU_CANH_BAO)

    def tao_hang(self, cha, nhan, gia_tri, mau=MAU_CHU_CHINH):
        h = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
        h.pack(fill="x", pady=4)
        ctk.CTkLabel(h, text=nhan, font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(side="left")
        n = ctk.CTkLabel(h, text=gia_tri, font=FONT_NOI_DUNG_BOLD, text_color=mau)
        n.pack(side="right")
        return n

    def tao_cot_goi_y(self, cha):
        cot = ctk.CTkFrame(cha, fg_color=MAU_NEN_SANG)
        cot.grid(row=0, column=1, sticky="nsew")
        cot.grid_rowconfigure((0, 1), weight=1)
        cot.grid_columnconfigure(0, weight=1)
        self.khung_nguy_co = self.tao_danh_sach(cot, 0, "Cảnh báo nguy cơ")
        self.khung_goi_y = self.tao_danh_sach(cot, 1, "Gợi ý khắc phục")

    def tao_danh_sach(self, cha, row, tieu_de):
        the = The(cha)
        the.grid(row=row, column=0, sticky="nsew", pady=(0, 15))
        k = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        k.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(k, text=tieu_de, font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", pady=(0, 10))
        return k

    def cap_nhat_ds(self, khung, muc, mau):
        for c in khung.winfo_children():
            if isinstance(c, ctk.CTkFrame): c.destroy()
        h = ctk.CTkFrame(khung, fg_color=MAU_THE_BG)
        h.pack(fill="x", pady=4)
        ctk.CTkLabel(h, text=f"• {muc}", font=FONT_NOI_DUNG, text_color=mau, wraplength=250, justify="left").pack(side="left")

    def tao_the_lich_su(self, cha):
        the = The(cha)
        the.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(the, text="Lịch sử cảnh báo", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", padx=25, pady=10)
        self.ls = ctk.CTkScrollableFrame(the, fg_color=MAU_THE_BG)
        self.ls.pack(fill="both", expand=True, padx=20, pady=10)

    def cap_nhat_giao_dien(self):
        self.after(0, self._render)

    def _render(self):
        if not self._ds.device_id: return
        du_lieu = self._ds.current_data
        cai_dat = self._ds.settings
        if du_lieu:
            nhiet_do = float(du_lieu.get("temp", 0))
            do_am = float(du_lieu.get("humidity", 0))
            trang_thai = self._ds.get_status(nhiet_do, do_am)
            mau = mau_theo_muc(trang_thai)

            self.nhan_nhiet_do.configure(text=f"{nhiet_do:.1f}°C", text_color=mau_theo_nhiet_do(nhiet_do))
            self.nhan_do_am.configure(text=f"{do_am:.0f}%")
            self.nhan_cam_bien.configure(text=self._ds.device_id)
            self.nhan_nguong.configure(text=f"{cai_dat.warning_threshold:.1f}°C")
            self.huy_hieu.configure(text=trang_thai, fg_color=mau)
            self.nhan_ghi_chu.configure(text=BANG_TRANG_THAI.get(trang_thai, "Đang chờ..."))
            self.cap_nhat_ds(self.khung_nguy_co, BANG_NGUY_CO.get(trang_thai, "Không xác định"), mau)
            self.cap_nhat_ds(self.khung_goi_y, self._ds.ai_suggestion or "Đang phân tích...", mau)

        for c in self.ls.winfo_children(): c.destroy()
        for canh_bao in self._ds.alerts:
            d = ctk.CTkFrame(self.ls, fg_color=MAU_THE_BG)
            d.pack(fill="x", pady=5)
            ts = canh_bao.get("timestamp", "").split("T")[-1][:5]
            lv = canh_bao.get("level", "WARNING").upper()
            ctk.CTkLabel(d, text=ts, font=FONT_NOI_DUNG_BOLD, width=50).pack(side="left")
            HuyHieu(d, text=lv, mau=mau_theo_muc(lv)).pack(side="left", padx=10)
            ctk.CTkLabel(d, text=canh_bao.get("warning", "Cảnh báo"), text_color=MAU_CHU_PHU).pack(side="left", padx=10)
            ctk.CTkLabel(d, text=f"{canh_bao.get('temp', '--')}°C", font=FONT_NOI_DUNG_BOLD).pack(side="right", padx=10)
        self.nhan_thoi_gian.configure(text=f"Cập nhật: {datetime.now().strftime('%H:%M:%S')}")

__all__ = ["AlertView"]