from utils.ai_client import goi_ai


def tao_goi_y_ha_nhiet(nhiet_do_hien_tai: float, nhiet_do_trung_binh: float, nguong: float) -> str:
    """Tạo gợi ý xử lý khi nhiệt độ vượt ngưỡng."""
    phan_tram_tang = 0.0
    if nhiet_do_trung_binh > 0:
        phan_tram_tang = (nhiet_do_hien_tai - nhiet_do_trung_binh) / nhiet_do_trung_binh * 100

    prompt = (
        "Hãy gợi ý hành động hạ nhiệt ngắn gọn. "
        f"Nhiệt độ hiện tại: {nhiet_do_hien_tai}. "
        f"Nhiệt độ trung bình: {nhiet_do_trung_binh}. "
        f"Phần trăm tăng: {phan_tram_tang:.2f}%. "
        f"Ngưỡng: {nguong}%. "
        "Trả lời ngắn gọn, dễ hiểu."
    )

    goi_y = goi_ai(prompt)
    if goi_y:
        return goi_y

    if phan_tram_tang >= nguong:
        return "Cần bật quạt hoặc giảm tải nhiệt ngay. Kiểm tra cảm biến và thông gió."

    return "Nhiệt độ ổn định. Tiếp tục theo dõi."
