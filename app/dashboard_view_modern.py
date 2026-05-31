"""
Bảng điều khiển hệ thống quản lý nhiệt độ hiện đại
Xây dựng với CustomTkinter và Matplotlib
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import Canvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# Bảng màu
MAU_NEN_SANG = "#F3F4F6"
MAU_THANH_BEN = "#FFFFFF"
MAU_THE_BG = "#FFFFFF"
MAU_CHINH = "#3B82F6"
MAU_CHINH_HOVER = "#2563EB"
MAU_CHU_CHINH = "#1F2937"
MAU_CHU_PHU = "#6B7280"
MAU_DUONG_BIEN = "#E5E7EB"
MAU_CANH_BAO = "#F59E0B"
MAU_NGUY_HIEM = "#EF4444"
MAU_THANH_CONG = "#10B981"

# Màu gradient nhiệt độ
MAU_GRADIENT = ["#FFE0E0", "#FFB3B3", "#FF8C8C", "#FF6666", "#FF4444"]


class ChiBaoTron(tk.Canvas):
    """Chỉ báo tròn tùy chỉnh với hiệu ứng gradient"""
    
    def __init__(self, parent, gia_tri, gia_tri_max=50, **kwargs):
        super().__init__(parent, **kwargs)
        self.gia_tri = gia_tri
        self.gia_tri_max = gia_tri_max
        self.ve_tron()
    
    def ve_tron(self):
        """Vẽ chỉ báo tròn dựa trên giá trị nhiệt độ"""
        ban_kinh = 25
        tam_x = 35
        tam_y = 35
        
        # Xác định màu dựa trên giá trị
        if self.gia_tri < 20:
            mau = "#4CAF50"  # Xanh lá
        elif self.gia_tri < 25:
            mau = "#8BC34A"  # Xanh lá nhạt
        elif self.gia_tri < 30:
            mau = "#FFC107"  # Vàng
        elif self.gia_tri < 35:
            mau = "#FF9800"  # Cam
        else:
            mau = "#F44336"  # Đỏ
        
        # Vẽ vòng tròn ngoài (nền)
        self.create_oval(tam_x - ban_kinh, tam_y - ban_kinh,
                        tam_x + ban_kinh, tam_y + ban_kinh,
                        fill="#E0E0E0", outline="#CCCCCC", width=1)
        
        # Vẽ vòng tròn trong (chỉ báo giá trị)
        ban_kinh_trong = ban_kinh * 0.8
        self.create_oval(tam_x - ban_kinh_trong, tam_y - ban_kinh_trong,
                        tam_x + ban_kinh_trong, tam_y + ban_kinh_trong,
                        fill=mau, outline=mau, width=0)
        
        # Vẽ giá trị
        self.create_text(tam_x, tam_y, text=f"{self.gia_tri}°C",
                        font=("Arial", 10, "bold"), fill="white")


class BangDieuKhienNhietDo:
    """Ứng dụng bảng điều khiển chính"""
    
    def __init__(self, cua_so_chinh):
        self.cua_so_chinh = cua_so_chinh
        self.cua_so_chinh.title("Hệ Thống Quản Lý Nhiệt Độ")
        self.cua_so_chinh.geometry("1400x800")
        
        # Đặt chế độ giao diện
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Dữ liệu mẫu - Khởi tạo trước
        self.nhiet_do_hien_tai = 30
        self.do_am = 65
        self.nguong_canh_bao = 35
        
        # Cấu hình lưới căn cứ
        self.cua_so_chinh.grid_rowconfigure(0, weight=1)
        self.cua_so_chinh.grid_columnconfigure(0, weight=0)
        self.cua_so_chinh.grid_columnconfigure(1, weight=1)
        
        # Tạo thanh bên
        self.tao_thanh_ben()
        
        # Tạo vùng nội dung chính
        self.tao_noi_dung_chinh()
        
        # Cập nhật với dữ liệu mẫu
        self.cap_nhat_bang_dieu_khien()
    
    def tao_thanh_ben(self):
        """Tạo thanh bên trái với điều hướng"""
        thanh_ben = ctk.CTkFrame(self.cua_so_chinh, fg_color=MAU_THANH_BEN, corner_radius=0)
        thanh_ben.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        thanh_ben.grid_propagate(False)
        thanh_ben.configure(width=220)
        
        # Tiêu đề
        tieu_de = ctk.CTkLabel(
            thanh_ben,
            text="HỆ THỐNG\nQUẢN LÝ\nNHIỆT ĐỘ",
            font=("Arial", 16, "bold"),
            text_color=MAU_CHINH,
            justify="center"
        )
        tieu_de.pack(pady=30, padx=20)
        
        # Đường ngăn cách
        duong_ngan = ctk.CTkFrame(thanh_ben, height=1, fg_color=MAU_DUONG_BIEN)
        duong_ngan.pack(fill="x", padx=20, pady=10)
        
        # Nút điều hướng
        self.cac_nut_nav = {}
        cac_muc = [
            ("Dashboard", "📊"),
            ("Alerts", "🔔"),
            ("Settings", "⚙️")
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
                command=lambda l=nhan: self.xu_ly_click_nav(l)
            )
            nut.pack(fill="x", padx=15, pady=8)
            self.cac_nut_nav[nhan] = nut
        
        # Chân trang
        khung_chan = ctk.CTkFrame(thanh_ben, fg_color="transparent")
        khung_chan.pack(side="bottom", fill="x", padx=20, pady=20)
        
        nhan_chan = ctk.CTkLabel(
            khung_chan,
            text="v1.0 | 2026",
            font=("Arial", 10),
            text_color=MAU_CHU_PHU
        )
        nhan_chan.pack()
    
    def xu_ly_click_nav(self, nhan):
        """Xử lý sự kiện nhấp nút điều hướng"""
        # Cập nhật kiểu nút
        for nhan_nut, nut in self.cac_nut_nav.items():
            if nhan_nut == nhan:
                nut.configure(fg_color=MAU_CHINH, text_color="white")
            else:
                nut.configure(fg_color="transparent", text_color=MAU_CHINH)
        
        print(f"Điều hướng đến: {nhan}")
    
    def tao_noi_dung_chinh(self):
        """Tạo vùng nội dung chính với các thẻ"""
        khung_chinh = ctk.CTkFrame(self.cua_so_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_chinh.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        khung_chinh.grid_rowconfigure(0, weight=0)
        khung_chinh.grid_rowconfigure(1, weight=1)
        khung_chinh.grid_columnconfigure(0, weight=1)
        
        # Tiêu đề
        self.tao_tieu_de(khung_chinh)
        
        # Vùng nội dung
        khung_noi_dung = ctk.CTkFrame(khung_chinh, fg_color=MAU_NEN_SANG, corner_radius=0)
        khung_noi_dung.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        khung_noi_dung.grid_rowconfigure(0, weight=0)
        khung_noi_dung.grid_rowconfigure(1, weight=1)
        khung_noi_dung.grid_columnconfigure(0, weight=1)
        khung_noi_dung.grid_columnconfigure(1, weight=1)
        
        # Hàng trên: Thẻ trạng thái và thẻ biểu đồ
        khung_tren = ctk.CTkFrame(khung_noi_dung, fg_color=MAU_NEN_SANG)
        khung_tren.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 20))
        khung_tren.grid_columnconfigure(0, weight=0)
        khung_tren.grid_columnconfigure(1, weight=1)
        
        self.tao_the_trang_thai(khung_tren)
        self.tao_the_bieu_do(khung_tren)
        
        # Hàng dưới: Thẻ dòng thời gian
        self.tao_the_dong_thoi_gian(khung_noi_dung)
    
    def tao_tieu_de(self, cha):
        """Tạo tiêu đề với ngày giờ"""
        tieu_de = ctk.CTkFrame(cha, fg_color=MAU_NEN_SANG, corner_radius=0)
        tieu_de.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        tieu_de.grid_columnconfigure(0, weight=1)
        
        nhan_tieu_de = ctk.CTkLabel(
            tieu_de,
            text="Bảng Điều Khiển",
            font=("Arial", 28, "bold"),
            text_color=MAU_CHU_CHINH
        )
        nhan_tieu_de.pack(side="left", anchor="w")
        
        thoi_gian = ctk.CTkLabel(
            tieu_de,
            text=datetime.now().strftime("%d/%m/%Y • %H:%M"),
            font=("Arial", 12),
            text_color=MAU_CHU_PHU
        )
        thoi_gian.pack(side="right", anchor="e")
    
    def tao_the_trang_thai(self, cha):
        """Tạo thẻ trạng thái nhiệt độ"""
        the = ctk.CTkFrame(
            cha,
            fg_color=MAU_THE_BG,
            corner_radius=15,
            border_width=1,
            border_color=MAU_DUONG_BIEN
        )
        the.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        the.grid_propagate(False)
        the.configure(width=280, height=280)
        
        # Khung lót
        trong = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        trong.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Tiêu đề
        nhan_tieu_de = ctk.CTkLabel(
            trong,
            text="Nhiệt độ hiện tại",
            font=("Arial", 14),
            text_color=MAU_CHU_PHU
        )
        nhan_tieu_de.pack(anchor="w", pady=(0, 15))
        
        # Giá trị nhiệt độ lớn
        self.nhan_nhiet_do = ctk.CTkLabel(
            trong,
            text=f"{self.nhiet_do_hien_tai}°C",
            font=("Arial", 70, "bold"),
            text_color=MAU_CHINH
        )
        self.nhan_nhiet_do.pack(pady=(10, 20))
        
        # Đường ngăn cách
        duong_ngan = ctk.CTkFrame(trong, height=1, fg_color=MAU_DUONG_BIEN)
        duong_ngan.pack(fill="x", pady=15)
        
        # Phần thông tin
        khung_thong_tin = ctk.CTkFrame(trong, fg_color=MAU_THE_BG)
        khung_thong_tin.pack(fill="x")
        
        # Độ ẩm
        khung_do_am = ctk.CTkFrame(khung_thong_tin, fg_color=MAU_THE_BG)
        khung_do_am.pack(fill="x", pady=5)
        
        nhan_do_am = ctk.CTkLabel(
            khung_do_am,
            text="Độ ẩm:",
            font=("Arial", 11),
            text_color=MAU_CHU_PHU
        )
        nhan_do_am.pack(side="left")
        
        self.nhan_gia_tri_do_am = ctk.CTkLabel(
            khung_do_am,
            text=f"{self.do_am}%",
            font=("Arial", 11, "bold"),
            text_color=MAU_CHU_CHINH
        )
        self.nhan_gia_tri_do_am.pack(side="right")
        
        # Ngưỡng cảnh báo
        khung_nguong = ctk.CTkFrame(khung_thong_tin, fg_color=MAU_THE_BG)
        khung_nguong.pack(fill="x", pady=5)
        
        nhan_nguong = ctk.CTkLabel(
            khung_nguong,
            text="Ngưỡng cảnh báo:",
            font=("Arial", 11),
            text_color=MAU_CHU_PHU
        )
        nhan_nguong.pack(side="left")
        
        self.nhan_gia_tri_nguong = ctk.CTkLabel(
            khung_nguong,
            text=f"{self.nguong_canh_bao}°C",
            font=("Arial", 11, "bold"),
            text_color=MAU_NGUY_HIEM if self.nhiet_do_hien_tai > self.nguong_canh_bao else MAU_CHU_CHINH
        )
        self.nhan_gia_tri_nguong.pack(side="right")
    
    def tao_the_bieu_do(self, cha):
        """Tạo thẻ biểu đồ với Matplotlib nhúng"""
        the = ctk.CTkFrame(
            cha,
            fg_color=MAU_THE_BG,
            corner_radius=15,
            border_width=1,
            border_color=MAU_DUONG_BIEN
        )
        the.grid(row=0, column=1, sticky="nsew")
        
        # Tiêu đề
        khung_tieu_de = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        khung_tieu_de.pack(fill="x", padx=25, pady=20)
        
        nhan_tieu_de = ctk.CTkLabel(
            khung_tieu_de,
            text="Xu hướng nhiệt độ",
            font=("Arial", 14, "bold"),
            text_color=MAU_CHU_CHINH
        )
        nhan_tieu_de.pack(anchor="w")
        
        # Vùng chứa biểu đồ
        khung_bieu_do = ctk.CTkFrame(the, fg_color=MAU_NEN_SANG)
        khung_bieu_do.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Tạo hình Matplotlib
        hinh = Figure(figsize=(6, 3.5), dpi=100, facecolor=MAU_NEN_SANG)
        truc = hinh.add_subplot(111)
        
        # Dữ liệu mẫu - nhiệt độ theo giờ
        gio = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
        nhiet_do_list = [22, 24, 26, 28, 30, 32, 31, 29, 27]
        
        # Vẽ
        truc.plot(gio, nhiet_do_list, marker='o', linewidth=2.5, markersize=7,
               color=MAU_CHINH, markerfacecolor=MAU_CHINH, markeredgewidth=0)
        truc.fill_between(range(len(gio)), nhiet_do_list, alpha=0.1, color=MAU_CHINH)
        
        # Kiểu dáng
        truc.set_facecolor(MAU_NEN_SANG)
        truc.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        truc.set_ylabel('Nhiệt độ (°C)', fontsize=10, color=MAU_CHU_PHU)
        truc.set_xlabel('')
        truc.spines['top'].set_visible(False)
        truc.spines['right'].set_visible(False)
        truc.spines['left'].set_color(MAU_DUONG_BIEN)
        truc.spines['bottom'].set_color(MAU_DUONG_BIEN)
        truc.tick_params(colors=MAU_CHU_PHU, labelsize=9)
        
        # Nhúng vào Tkinter
        canvas = FigureCanvasTkAgg(hinh, master=khung_bieu_do)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.hinh_bieu_do = hinh
        self.canvas_bieu_do = canvas
    
    def tao_the_dong_thoi_gian(self, cha):
        """Tạo dòng thời gian với chỉ báo tròn nhiệt độ"""
        the = ctk.CTkFrame(
            cha,
             fg_color=MAU_THE_BG,
            corner_radius=15,
            border_width=1,
            border_color=MAU_DUONG_BIEN
        )
        the.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(20, 0))
        
        # Tiêu đề
        nhan_tieu_de = ctk.CTkLabel(
            the,
            text="Nhiệt độ theo giờ",
            font=("Arial", 14, "bold"),
            text_color=MAU_CHU_CHINH
        )
        nhan_tieu_de.pack(anchor="w", padx=25, pady=(20, 20))
        
        # Vùng chứa dòng thời gian
        khung_dong_thoi_gian = ctk.CTkFrame(the, fg_color=MAU_THE_BG)
        khung_dong_thoi_gian.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        # Dữ liệu mẫu cho dòng thời gian
        cac_gio = ['09:00', '12:00', '15:00', '18:00', '21:00', '24:00']
        nhiet_do_dong_thoi = [23, 28, 32, 29, 25, 22]
        
        # Tạo chỉ báo dòng thời gian
        for chi_so, (gio, nhiet_do) in enumerate(zip(cac_gio, nhiet_do_dong_thoi)):
            muc_thoi_gian = ctk.CTkFrame(khung_dong_thoi_gian, fg_color=MAU_THE_BG)
            muc_thoi_gian.pack(fill="x", pady=15)
            
            # Nhãn và vòng tròn trong bố cục ngang
            nhan_gio = ctk.CTkLabel(
                muc_thoi_gian,
                text=gio,
                font=("Arial", 11, "bold"),
                text_color=MAU_CHU_CHINH,
                width=60
            )
            nhan_gio.pack(side="left", padx=(0, 20))
            
            # Tạo chỉ báo tròn sử dụng Canvas
            canvas_chi_bao = ChiBaoTron(
                muc_thoi_gian,
                nhiet_do,
                width=70,
                height=70,
                bg=MAU_THE_BG,
                highlightthickness=0
            )
            canvas_chi_bao.pack(side="left", padx=10)
            
            # Nhãn giá trị nhiệt độ
            nhan_nhiet_do = ctk.CTkLabel(
                muc_thoi_gian,
                text=f"{nhiet_do}°C",
                font=("Arial", 11),
                text_color=MAU_CHU_PHU
            )
            nhan_nhiet_do.pack(side="left", padx=20)
            
            # Thanh tiến trình (chỉ báo trực quan)
            gia_tri_tien_trinh = min(nhiet_do / 40.0, 1.0)  # Chuẩn hóa đến 40°C tối đa
            thanh_tien_trinh = ctk.CTkProgressBar(
                muc_thoi_gian,
                fg_color=MAU_DUONG_BIEN,
                progress_color=self.lay_mau_theo_nhiet_do(nhiet_do),
                height=6,
                corner_radius=3
            )
            thanh_tien_trinh.pack(side="left", fill="x", expand=True, padx=20)
            thanh_tien_trinh.set(gia_tri_tien_trinh)
    
    def lay_mau_theo_nhiet_do(self, nhiet_do):
        """Lấy màu dựa trên giá trị nhiệt độ"""
        if nhiet_do < 20:
            return "#4CAF50"  # Xanh lá
        elif nhiet_do < 25:
            return "#8BC34A"  # Xanh lá nhạt
        elif nhiet_do < 30:
            return "#FFC107"  # Vàng
        elif nhiet_do < 35:
            return "#FF9800"  # Cam
        else:
            return "#F44336"  # Đỏ
    
    def cap_nhat_bang_dieu_khien(self):
        """Cập nhật bảng điều khiển với dữ liệu mới"""
        # Phương thức này có thể được gọi để cập nhật các giá trị động
        pass


def main():
    """Điểm vào chương trình"""
    cua_so_chinh = ctk.CTk()
    ung_dung = BangDieuKhienNhietDo(cua_so_chinh)
    cua_so_chinh.mainloop()


if __name__ == "__main__":
    main()
