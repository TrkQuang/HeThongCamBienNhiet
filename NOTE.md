# NOTE.md - Ghi chú kỹ thuật

## Công nghệ sử dụng

- Thiết bị: ESP8266/ESP32 + DHT11/DHT22
- Giao tiếp: HTTP REST (JSON)
- Backend: Python 3.11+ + Flask
- UI desktop: Tkinter hoặc PyQt
- Database: SQLite (có thể mở rộng MySQL/PostgreSQL)

## Lưu ý kỹ thuật

### Đồng bộ thời gian

- Thiết bị nên lấy thời gian NTP định kỳ để giảm lệch.
- Server luôn ghi thêm `server_ts` để đối chiếu độ trễ.
- Chuẩn hóa timezone về UTC.

### Xử lý mất kết nối

- Thiết bị có bộ đệm nhỏ, retry theo backoff.
- API chấp nhận dữ liệu gửi bù (late data) kèm timestamp.
- Ghi log sự kiện mất kết nối để kiểm tra sau.

### Hiệu năng khi nhận data liên tục

- Ghi DB theo lô (batch) thay vì từng bản ghi.
- Giới hạn tần suất gửi (ví dụ 2-5 giây/điểm).
- Tách luồng nhận dữ liệu và luồng xử lý tính toán.

## Ngưỡng cảnh báo (10-15%)

- Mức cảnh báo mặc định: 10%.
- Mức cảnh báo cao: 15%.
- Nên cấu hình trong `config/settings.yaml`.
