"""
Chuong trinh chinh cho He Thong Quan Ly Nhiet Do
"""

from .main_window import MainWindow


def chay_ung_dung():
    cua_so = MainWindow()
    cua_so.mainloop()


if __name__ == "__main__":
    chay_ung_dung()


