# LuongHD.md - Luồng hoạt động tổng thể

## Mục tiêu

Mô tả luồng đi của dữ liệu từ thiết bị đến UI, và vai trò từng module (IoT -> API -> Core -> DB -> UI).

## 1) Luồng dữ liệu chính

1. Thiết bị đọc nhiệt độ (DHT) và tạo payload JSON.
2. Gửi HTTP POST đến API (/api/du-lieu-nhiet).
3. API nhận payload, validate, gọi core xử lý.
4. Core xử lý (chuẩn hóa, gắn thời gian server, tính cảnh báo).
5. Database lưu readings/alerts (nếu có).
6. UI gọi API GET để lấy dữ liệu và cảnh báo.
7. UI hiển thị realtime và thông báo cảnh báo.

## 2) Vai trò từng module

### IoT

- Đọc cảm biến và gửi dữ liệu lên API.
- Đảm bảo payload đúng chuẩn: sensor_id, temp, ts, device_id.

### API (Flask)

- Nhận request, validate payload.
- Gọi core xử lý dữ liệu.
- Trả response và (nếu có) lưu DB qua repository.

### Core

- Chuẩn hóa dữ liệu, gắn thời gian server.
- Tính trung bình, % tăng, xác định cảnh báo.

### Database

- Lưu readings, alerts, thông tin cảm biến.
- Hỗ trợ truy vấn cho UI.

### UI (Tkinter)

- Gọi API GET để lấy dữ liệu mới nhất.
- Hiển thị bảng/biểu đồ và danh sách cảnh báo.

## 3) Luồng xử lý chi tiết (API -> Core -> DB -> UI)

Tóm tắt: **IoT → API → Core → Database → API → App(UI)**.

1. **IoT** tạo payload JSON từ dữ liệu cảm biến.

- Bắt buộc: `sensor_id`, `temp`, `ts`, `device_id`.
- Khuyến nghị: đồng bộ NTP để `ts` chính xác.

2. **API** nhận request (POST /api/du-lieu-nhiet).

- Parse JSON và kiểm tra schema.
- Validate rule cơ bản (range nhiệt độ/độ ẩm).
- Nếu lỗi: trả response lỗi rõ ràng.

3. **Core** xử lý dữ liệu.

- Chuẩn hóa dữ liệu, gắn `server_ts`.
- Tính trung bình và % tăng nếu có dữ liệu lịch sử.
- So sánh ngưỡng để tạo cảnh báo.

4. **Database** lưu dữ liệu.

- Lưu readings và alerts (nếu có).
- Đảm bảo truy vấn nhanh theo sensor và thời gian.

5. **API** trả response cho IoT.

- Trả trạng thái thành công và dữ liệu đã chuẩn hóa.

6. **UI** gọi API GET để lấy dữ liệu mới nhất.

- Polling theo chu kỳ (ví dụ 2-5 giây).
- Parse response và cập nhật dashboard/cảnh báo.

7. **UI** cập nhật hiển thị realtime và trạng thái hệ thống.

## 4) Ví dụ payload

```
{
  "sensor_id": "S01",
  "temp": 32.5,
  "humidity": 60,
  "ts": "2026-05-10T10:00:00Z",
  "device_id": "ESP32-01"
}
```

## 5) Ví dụ response

```
{
  "status": "success",
  "message": "Đã nhận dữ liệu",
  "data": {
    "item": {
      "sensor_id": "S01",
      "temp": 32.5,
      "humidity": 60,
      "ts": "2026-05-10T10:00:00Z",
      "server_ts": "2026-05-10T10:00:01Z"
    }
  }
}
```

## 6) Ghi chú

- Nếu chưa có thiết bị, có thể gửi payload bằng Postman/curl.
- Nên giảm tần suất gửi để tránh quá tải.
