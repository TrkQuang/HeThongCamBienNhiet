"""
Chương trình chính cho Hệ Thống Quản Lý Nhiệt Độ
"""

import customtkinter as ctk
from dashboard_view_modern import BangDieuKhienNhietDo

def chay_ung_dung():
    """Hàm chính để chạy ứng dụng"""
    # Tạo cửa sổ chính
    cua_so_chinh = ctk.CTk()
    
    # Tạo bảng điều khiển
    bang_dieu_khien = BangDieuKhienNhietDo(cua_so_chinh)
    
    # Chạy vòng lặp sự kiện
    cua_so_chinh.mainloop()


<<<<<<< HEAD
if __name__ == "__main__":
    chay_ung_dung()
=======
root.mainloop()
>>>>>>> e3bd3e95ff4fe7e0c6a94614528049f56ad51bd0
