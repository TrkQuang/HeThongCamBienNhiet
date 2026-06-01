import customtkinter as ctk

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

FONT_TIEU_DE = ("Arial", 28, "bold")
FONT_TIEU_DE_THE = ("Arial", 14, "bold")
FONT_NOI_DUNG = ("Arial", 11)
FONT_NOI_DUNG_BOLD = ("Arial", 11, "bold")
FONT_NHAN = ("Arial", 12)
FONT_SO_LON = ("Arial", 70, "bold")


def ap_dung_giao_dien():
	ctk.set_appearance_mode("light")
	ctk.set_default_color_theme("blue")


def mau_theo_nhiet_do(nhiet_do):
	if nhiet_do < 20:
		return "#4CAF50"
	if nhiet_do < 25:
		return "#8BC34A"
	if nhiet_do < 30:
		return "#FFC107"
	if nhiet_do < 35:
		return "#FF9800"
	return "#F44336"


def mau_theo_muc(muc):
	muc = muc.lower()
	if muc in {"danger", "high", "nguy hiem", "nguy hiểm"}:
		return MAU_NGUY_HIEM
	if muc in {"warning", "warn", "canh bao", "cảnh báo"}:
		return MAU_CANH_BAO
	return MAU_THANH_CONG


class The(ctk.CTkFrame):
	def __init__(self, master, **kwargs):
		super().__init__(
			master,
			fg_color=MAU_THE_BG,
			corner_radius=15,
			border_width=1,
			border_color=MAU_DUONG_BIEN,
			**kwargs,
		)


class HuyHieu(ctk.CTkLabel):
	def __init__(self, master, text, mau):
		super().__init__(
			master,
			text=text,
			text_color="white",
			fg_color=mau,
			corner_radius=10,
			padx=10,
			pady=4,
			font=FONT_NOI_DUNG_BOLD,
		)
