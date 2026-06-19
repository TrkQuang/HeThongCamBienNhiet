"""
Bang canh bao nhiet do - giao dien hien dai
"""

import threading
from typing import Optional, List, Dict, Any
import customtkinter as ctk
from datetime import datetime

from .data_service import DataService
from .widgets import (
    MAU_NEN_SANG,
    MAU_THE_BG,
    MAU_CHINH,
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
    HuyHieu,
    mau_theo_nhiet_do,
    mau_theo_muc,
)

class AlertView(ctk.CTkFrame):
    def __init__(self, parent, data_service: DataService):
        super().__init__(parent, fg_color=MAU_NEN_SANG)
        self._ds = data_service
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tao_noi_dung()
        
        # Subscribe to centralized updates
        self._ds.subscribe(self.cap_nhat_giao_dien)

    def tao_noi_dung(self):
        khung_chinh = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_chinh.grid(row=0, column=0, sticky="nsew")
        khung_chinh.grid_rowconfigure(0, weight=0)
        khung_chinh.grid_rowconfigure(1, weight=1)
        khung_chinh.grid_columnconfigure(0, weight=1)

        self.tao_tieu_de(khung_chinh)

        khung_noi_dung = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_noi_dung.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        khung_noi_dung.grid_rowconfigure(0, weight=0)
        khung_noi_dung.grid_rowconfigure(1, weight=1)
        khung_noi_dung.grid_columnconfigure(0, weight=1)

        khung_tren = ctk.CTkFrame(khung_noi_dung, fg_color=MAU_NEN_SANG)
        khung_tren.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        khung_tren.grid_columnconfigure(0, weight=2)
        khung_tren.grid_columnconfigure(1, weight=1)

        self.tao_the_trang_thai(khung_tren)
        self.tao_cot_goi_y(khung_tren)
        self.tao_the_lich_su(khung_noi_dung)

    def tao_tieu_de(self, cha):
        tieu_de = ctk.CTkFrame(cha, fg_color=MAU_NEN_SANG, corner_radius=0)
        tieu_de.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        tieu_de.grid_columnconfigure(0, weight=1)

        nhan_tieu_de = ctk.CTkLabel(
            tieu_de,
            text="Cảnh Báo",
            font=FONT_TIEU_DE,
            text_color=MAU_CHU_CHINH,
        )
        nhan_tieu_de.pack(side="left", anchor="w")

        self.nhan_thoi_gian = ctk.CTkLabel(
            tieu_de,
            text=f"Cập nhật: {datetime.now().strftime('%d/%m/%Y • %H:%M')}",
            font=FONT_NHAN,
            text_color=MAU_CHU_PHU,
        )
        self.nhan_thoi_gian.pack(side="right", anchor="e")

    def tao_the_trang_thai(self, cha):
        the = The(cha)
        the.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        trong = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        trong.pack(fill="both", expand=True, padx=25, pady=25)

        nhan_tieu_de = ctk.CTkLabel(
            trong,
            text="Tình trạng hiện tại",
            font=FONT_TIEU_DE_THE,
            text_color=MAU_CHU_PHU,
        )
        nhan_tieu_de.pack(anchor="w", pady=(0, 10))

        self.nhan_nhiet_do = ctk.CTkLabel(
            trong,
            text="--°C",
            font=FONT_SO_LON,
            text_color=MAU_CHINH,
        )
        self.nhan_nhiet_do.pack(anchor="w", pady=(0, 10))

        hang_muc_do = ctk.CTkFrame(trong, fg_color=MAU_THE_BG)
        hang_muc_do.pack(fill="x", pady=(0, 10))

        self.nhan_ghi_chu = ctk.CTkLabel(
            hang_muc_do,
            text="Đang chờ dữ liệu...",
            font=FONT_NOI_DUNG,
            text_color=MAU_CHU_CHINH,
        )
        self.nhan_ghi_chu.pack(side="left")

        self.huy_hieu = HuyHieu(hang_muc_do, text="NORMAL", mau=MAU_THANH_CONG)
        self.huy_hieu.pack(side="right")

        duong_ngan = ctk.CTkFrame(trong, height=1, fg_color=MAU_DUONG_BIEN)
        duong_ngan.pack(fill="x", pady=15)

        self.nhan_cam_bien = self.tao_hang_thong_tin(trong, "Cảm biến:", "--")
        self.nhan_vi_tri = self.tao_hang_thong_tin(trong, "Vị trí:", "--")
        self.nhan_do_am = self.tao_hang_thong_tin(trong, "Độ ẩm:", "--%")
        self.nhan_nguong = self.tao_hang_thong_tin(trong, "Ngưỡng cảnh báo:", "--°C", MAU_CANH_BAO)

    def tao_hang_thong_tin(self, cha, nhan, gia_tri, mau=None):
        hang = ctk.CTkFrame(cha, fg_color=MAU_THE_BG)
        hang.pack(fill="x", pady=4)

        nhan_trai = ctk.CTkLabel(hang, text=nhan, font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU)
        nhan_trai.pack(side="left")

        nhan_phai = ctk.CTkLabel(hang, text=gia_tri, font=FONT_NOI_DUNG_BOLD, text_color=mau or MAU_CHU_CHINH)
        nhan_phai.pack(side="right")

        return nhan_phai

    def tao_cot_goi_y(self, cha):
        cot = ctk.CTkFrame(cha, fg_color=MAU_NEN_SANG)
        cot.grid(row=0, column=1, sticky="nsew")
        cot.grid_rowconfigure(0, weight=1)
        cot.grid_rowconfigure(1, weight=1)
        cot.grid_columnconfigure(0, weight=1)

        self.khung_nguy_co = self.tao_the_danh_sach(cot, 0, "Cảnh báo nguy cơ", ["Ổn định"], MAU_NGUY_HIEM)
        self.khung_goi_y = self.tao_the_danh_sach(cot, 1, "AI Suggester (Gợi ý)", ["Đang phân tích..."], MAU_CHINH)

    def tao_the_danh_sach(self, cha, dong, tieu_de, danh_sach, mau):
        the = The(cha)
        the.grid(row=dong, column=0, sticky="nsew", pady=(0, 15))

        khung = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        khung.pack(fill="both", expand=True, padx=20, pady=20)

        nhan_tieu_de = ctk.CTkLabel(khung, text=tieu_de, font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH)
        nhan_tieu_de.pack(anchor="w", pady=(0, 10))

        self.cap_nhat_danh_sach(khung, danh_sach, mau)
        return khung

    def cap_nhat_danh_sach(self, khung, danh_sach, mau):
        for child in khung.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                child.destroy()

        for muc in danh_sach:
            hang = ctk.CTkFrame(khung, fg_color=MAU_THE_BG)
            hang.pack(fill="x", pady=4)

            nhan = ctk.CTkLabel(hang, text=f"• {muc}", font=FONT_NOI_DUNG, text_color=mau, wraplength=250, justify="left")
            nhan.pack(side="left")

    def tao_the_lich_su(self, cha):
        the = The(cha)
        the.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        the.grid_rowconfigure(1, weight=1)
        the.grid_columnconfigure(0, weight=1)

        nhan_tieu_de = ctk.CTkLabel(the, text="Lịch sử cảnh báo", font=FONT_TIEU_DE_THE, text_color=MAU_CHU_CHINH)
        nhan_tieu_de.pack(anchor="w", padx=25, pady=(20, 10))

        self.khung_lich_su = ctk.CTkScrollableFrame(the, fg_color=MAU_THE_BG)
        self.khung_lich_su.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def cap_nhat_giao_dien(self):
        self.after(0, self._render_ui)

    def _render_ui(self):
        alerts = self._ds.alerts
        current = self._ds.current_data
        settings = self._ds.settings
        ai_suggestion = self._ds.ai_suggestion
        device_id = self._ds.device_id

        if not device_id:
            self.nhan_ghi_chu.configure(text="Vui lòng chọn thiết bị")
            return

        # 1. Update Current Stats
        if current:
            temp = float(current.get("temp", 0))
            self.nhan_nhiet_do.configure(text=f"{temp:.1f}°C", text_color=mau_theo_nhiet_do(temp))
            self.nhan_do_am.configure(text=f"{float(current.get('humidity', 0)):.0f}%")
            self.nhan_cam_bien.configure(text=device_id)
            self.nhan_vi_tri.configure(text=f"Vị trí {device_id}")
            self.nhan_nguong.configure(text=f"{settings.warning_threshold:.1f}°C")

        # 2. Update Alerts Status
        # Use current data to determine status, not historical alerts
        current_status = "NORMAL"
        current_temp = 0
        current_hum = 0
        
        if current:
            current_temp = float(current.get("temp", 0))
            current_hum = float(current.get("humidity", 0))
            current_status = self._ds._determine_status(current_temp, current_hum)
        
        # Update status indicator based on current status
        self.huy_hieu.configure(text=current_status.upper(), fg_color=mau_theo_muc(current_status))
        
        # Set message based on current status
        if current_status == "NORMAL":
            self.nhan_ghi_chu.configure(text="Hệ thống hoạt động bình thường")
        elif current_status == "WARNING":
            self.nhan_ghi_chu.configure(text="Nhiệt độ đã vượt ngưỡng cảnh báo")
        elif current_status == "DANGER":
            self.nhan_ghi_chu.configure(text="Nhiệt độ đang ở mức nguy hiểm")
        
        # Update risk alerts based on current status, not historical alerts
        if current_status == "NORMAL":
            self.cap_nhat_danh_sach(self.khung_nguy_co, ["Không có nguy cơ"], MAU_THANH_CONG)
        elif current_status == "WARNING":
            risks = ["Nhiệt độ vượt ngưỡng"]
            if current_hum >= settings.humidity_threshold:
                risks.append("Độ ẩm vượt ngưỡng")
            self.cap_nhat_danh_sach(self.khung_nguy_co, risks, MAU_CANH_BAO)
        elif current_status == "DANGER":
            risks = ["Nhiệt độ vượt ngưỡng nguy hiểm"]
            if current_hum >= settings.humidity_threshold:
                risks.append("Độ ẩm vượt ngưỡng")
            risks.append("Nguy cơ cháy nổ thiết bị")
            self.cap_nhat_danh_sach(self.khung_nguy_co, risks, MAU_NGUY_HIEM)
        else:
            self.cap_nhat_danh_sach(self.khung_nguy_co, ["Không có nguy cơ"], MAU_THANH_CONG)

        # 3. AI Suggestions
        ai_color = MAU_CHINH
        if current:
            temp = float(current.get("temp", 0))
            hum = float(current.get("humidity", 0))
            status = self._ds._determine_status(temp, hum)
            ai_color = mau_theo_muc(status)
        if ai_suggestion:
            self.cap_nhat_danh_sach(self.khung_goi_y, [ai_suggestion], ai_color)
        else:
            self.cap_nhat_danh_sach(self.khung_goi_y, ["Đang thu thập dữ liệu phân tích..."], MAU_CHU_PHU)

        # 4. History List
        self._render_lich_su(alerts)
        self.nhan_thoi_gian.configure(text=f"Cập nhật: {datetime.now().strftime('%H:%M:%S')}")

    def _render_lich_su(self, alerts):
        for child in self.khung_lich_su.winfo_children():
            child.destroy()
        
        if not alerts:
            ctk.CTkLabel(self.khung_lich_su, text="Chưa có cảnh báo nào.", text_color=MAU_CHU_PHU).pack(pady=20)
            return

        for item in alerts:
            dong = ctk.CTkFrame(self.khung_lich_su, fg_color=MAU_THE_BG)
            dong.pack(fill="x", pady=5)
            
            ts = item.get("timestamp") or item.get("created_at") or ""
            gio = ts.split("T")[-1][:5] if "T" in str(ts) else "--:--"
            
            ctk.CTkLabel(dong, text=gio, font=FONT_NOI_DUNG_BOLD, width=50).pack(side="left", padx=10)
            
            level = item.get("level") or "warning"
            HuyHieu(dong, text=str(level).upper(), mau=mau_theo_muc(level)).pack(side="left", padx=10)
            
            msg = item.get("warning") or item.get("message") or "Cảnh báo"
            ctk.CTkLabel(dong, text=msg, font=FONT_NOI_DUNG, text_color=MAU_CHU_PHU).pack(side="left", padx=10)
            
            temp = item.get("temp") or item.get("current_temp", "--")
            ctk.CTkLabel(dong, text=f"{temp}°C", font=FONT_NOI_DUNG_BOLD, text_color=MAU_CHU_CHINH).pack(side="right", padx=10)

__all__ = ["AlertView"]