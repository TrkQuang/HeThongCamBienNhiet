import customtkinter as ctk
from datetime import datetime
from .data_service import DataService
from .audio_service import play_warning_sound, stop_warning_sound
from .widgets import *


BANG_TRANG_THAI = {
    "NORMAL": "Bình thường",
    "WARNING": "Vượt ngưỡng",
    "DANGER": "Nguy hiểm!",
}
BANG_NGUY_CO = {
    "NORMAL": "An toàn",
    "WARNING": "Trung bình",
    "DANGER": "Nguy cơ cao",
}

class AlertView(ctk.CTkFrame):
    def __init__(self, parent, data_service: DataService):
        super().__init__(parent, fg_color=MAU_NEN_SANG)
        self._ds = data_service
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Track previous state for partial updates
        self._prev_status = ""
        self._prev_temp = ""
        self._prev_humidity = ""
        self._prev_device_id = ""
        self._prev_threshold = ""
        self._prev_warn = 0.0
        self._prev_danger = 0.0
        self._prev_risk = ""
        self._prev_suggestion = ""
        self._prev_suggestion_loading = False
        self._prev_suggestion_error = ""
        self._prev_alerts_len = -1
        self._prev_time_str = ""
        self._prev_sound_state = False
        self._prev_sound_status = ""

        # Reusable history row widgets: list of {"frame", "ts", "badge", "msg", "temp"}
        self._history_rows: list = []
        self._prev_refresh_version = -1

        self.tao_noi_dung()
        self._ds.subscribe(self.cap_nhat_giao_dien)

    # ── UI build (one shot) ────────────────────────────────────────────

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
        # Pre-create suggestion rows (up to 5)
        self._suggestion_labels = []
        self._risk_labels = []

    def tao_danh_sach(self, cha, row, tieu_de):
        the = The(cha)
        the.grid(row=row, column=0, sticky="nsew", pady=(0, 15))
        k = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        k.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(k, text=tieu_de, font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", pady=(0, 10))
        return k

    def cap_nhat_ds(self, khung, muc, mau):
        """Partial update: only change text content, never destroy frames.

        Clears content but keeps container widget hierarchy intact.
        """
        for c in khung.winfo_children():
            if isinstance(c, ctk.CTkFrame):
                c.destroy()

        lines = muc.split("\n") if "\n" in muc else [muc]
        for line in lines:
            h = ctk.CTkFrame(khung, fg_color=MAU_THE_BG)
            h.pack(fill="x", pady=4)
            ctk.CTkLabel(h, text=f"• {line.strip()}", font=FONT_NOI_DUNG,
                         text_color=mau, wraplength=250, justify="left").pack(side="left")

    def tao_the_lich_su(self, cha):
        the = The(cha)
        the.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(the, text="Lịch sử cảnh báo", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH).pack(anchor="w", padx=25, pady=10)
        self.ls = ctk.CTkScrollableFrame(the, fg_color=MAU_THE_BG)
        self.ls.pack(fill="both", expand=True, padx=20, pady=10)
        self._history_rows = []  # will be populated on first render

    # ── update cycle ──────────────────────────────────────────────────

    def cap_nhat_giao_dien(self):
        self.after(0, self._render)

    def _render(self):
        if not self._ds.device_id:
            return

        # Detect force_refresh → reset all _prev_* so full re-render happens
        if self._ds._refresh_version != self._prev_refresh_version:
            self._prev_refresh_version = self._ds._refresh_version
            self._prev_temp = ""
            self._prev_warn = 0.0
            self._prev_danger = 0.0
            self._prev_status = ""
            self._prev_threshold = ""
            self._prev_alerts_len = -1

        du_lieu = self._ds.current_data
        cai_dat = self._ds.settings

        if du_lieu:
            nhiet_do = float(du_lieu.get("temp", 0))
            do_am = float(du_lieu.get("humidity", 0))
            trang_thai = self._ds.get_status(nhiet_do, do_am)
            mau = mau_theo_muc(trang_thai)
            temp_str = f"{nhiet_do:.1f}°C"
            humidity_str = f"{do_am:.0f}%"
            threshold_str = f"{cai_dat.warning_threshold:.1f}°C"

            # ── partial update: only change when value differs ─────────
            warn_changed = cai_dat.warning_threshold != self._prev_warn
            danger_changed = cai_dat.danger_threshold != self._prev_danger

            if temp_str != self._prev_temp or warn_changed or danger_changed:
                self.nhan_nhiet_do.configure(
                    text=temp_str,
                    text_color=mau_theo_nguong(nhiet_do, cai_dat.warning_threshold, cai_dat.danger_threshold)
                )
                self._prev_temp = temp_str
                self._prev_warn = cai_dat.warning_threshold
                self._prev_danger = cai_dat.danger_threshold
            if humidity_str != self._prev_humidity:
                self.nhan_do_am.configure(text=humidity_str)
                self._prev_humidity = humidity_str
            if self._prev_device_id != self._ds.device_id:
                self.nhan_cam_bien.configure(text=self._ds.device_id)
                self._prev_device_id = self._ds.device_id
            if threshold_str != self._prev_threshold:
                self.nhan_nguong.configure(text=threshold_str)
                self._prev_threshold = threshold_str
            if trang_thai != self._prev_status or warn_changed or danger_changed:
                self.huy_hieu.configure(text=trang_thai, fg_color=mau)
                self.nhan_ghi_chu.configure(text=BANG_TRANG_THAI.get(trang_thai, "Đang chờ..."))
                self._prev_status = trang_thai

            # Risk (just a static text — always simple)
            risk = BANG_NGUY_CO.get(trang_thai, "Không xác định")
            if risk != self._prev_risk:
                self.cap_nhat_ds(self.khung_nguy_co, risk, mau)
                self._prev_risk = risk

            # ── AI suggestion with 3 states ────────────────────────────
            new_loading = self._ds.ai_loading
            new_error = self._ds.ai_error or ""
            if new_loading:
                sugg = "🔄 Đang tạo gợi ý..."
            elif new_error:
                sugg = f"⚠️ {new_error}"
            else:
                sugg = self._ds.ai_suggestion or "Không có gợi ý nào."

            # Only update if actually changed
            changed = (
                sugg != self._prev_suggestion
                or new_loading != self._prev_suggestion_loading
                or new_error != self._prev_suggestion_error
            )
            if changed:
                self.cap_nhat_ds(self.khung_goi_y, sugg, mau)
                self._prev_suggestion = sugg
                self._prev_suggestion_loading = new_loading
                self._prev_suggestion_error = new_error

            # ── sound ──────────────────────────────────────────────────
            if cai_dat.sound_alert:
                if trang_thai in ("DANGER", "WARNING"):
                    if self._prev_sound_status != trang_thai:
                        play_warning_sound()
                        self._prev_sound_status = trang_thai
                        self._prev_sound_state = True
                else:
                    if self._prev_sound_state or self._prev_sound_status:
                        stop_warning_sound()
                        self._prev_sound_state = False
                        self._prev_sound_status = ""
            elif self._prev_sound_state or self._prev_sound_status:
                stop_warning_sound()
                self._prev_sound_state = False
                self._prev_sound_status = ""
        # ── history: only recreate when count changes ──────────────────
        self._render_history()
        ts_now = f"Cập nhật: {datetime.now().strftime('%H:%M:%S')}"
        if ts_now != self._prev_time_str:
            self.nhan_thoi_gian.configure(text=ts_now)
            self._prev_time_str = ts_now

    def _render_history(self):
        alerts = self._ds.alerts
        n = len(alerts)
        if n == self._prev_alerts_len:
            return  # no change, skip
        self._prev_alerts_len = n

        for c in self.ls.winfo_children():
            c.destroy()
        self._history_rows.clear()

        for canh_bao in alerts:
            d = ctk.CTkFrame(self.ls, fg_color=MAU_THE_BG)
            d.pack(fill="x", pady=5)
            ts = canh_bao.get("timestamp", "").split("T")[-1][:5]
            lv = canh_bao.get("level", "WARNING").upper()
            ctk.CTkLabel(d, text=ts, font=FONT_NOI_DUNG_BOLD, width=50).pack(side="left")
            HuyHieu(d, text=lv, mau=mau_theo_muc(lv)).pack(side="left", padx=10)
            ctk.CTkLabel(d, text=canh_bao.get("warning", "Cảnh báo"), text_color=MAU_CHU_PHU).pack(side="left", padx=10)
            ctk.CTkLabel(d, text=f"{canh_bao.get('temp', '--')}°C", font=FONT_NOI_DUNG_BOLD).pack(side="right", padx=10)
            self._history_rows.append(d)


__all__ = ["AlertView"]
