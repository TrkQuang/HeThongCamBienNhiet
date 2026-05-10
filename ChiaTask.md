# ChiaTask.md - Phân công công việc (4 người)

## Công việc chung (bắt buộc cho cả 4 người)

- Đọc README tổng quan và NOTE.md.
- Nắm rõ logic tính toán:
  - avg = sum(temp) / n
  - percent = (current - avg) / avg \* 100
  - Cảnh báo nếu percent > 10
- Thống nhất format payload (sensor_id, temp, ts, device_id).
- Thống nhất cách chạy hệ thống (API + UI + IoT).

## Quy trình phối hợp IoT <-> API (bắt buộc)

- IoT chỉ cần gửi đúng payload và đúng URL API, không cần viết API.
- API chịu trách nhiệm nhận, validate và lưu DB.
- Cần thống nhất trước:
  - URL endpoint: /api/temperature
  - Payload JSON: sensor_id, temp, ts, device_id
  - Tần suất gửi (ví dụ 2-5 giây/lần)
  - Quy ước thời gian (UTC)
- Khi API thay đổi payload/URL thì IoT phải cập nhật lại firmware.

## Phân công chi tiết

### Nguyễn Phúc Tài - IoT (thiết bị)

- Lập trình ESP8266/ESP32 đọc nhiệt độ từ DHT (đúng chân, đúng thư viện).
- Kết nối Wi-Fi, cấu hình SSID/PASS và URL API.
- Tạo payload JSON chuẩn (sensor_id, temp, ts, device_id).
- Gửi dữ liệu qua HTTP POST định kỳ.
- Viết script Python `iot/payload_check.py` để kiểm tra payload trước khi gửi.
- Xử lý mất kết nối, retry/backoff và log Serial để debug.
- Đồng bộ thời gian NTP để có timestamp chính xác.
- Viết hướng dẫn nạp firmware, cấu hình và sơ đồ chân nối dây (iot/README.md).
- Phạm vi chính: firmware + hướng dẫn thiết bị, không làm API/UI/DB.

### Trần Kỳ Quang - API Flask

- Tạo endpoint /api/temperature và xử lý payload.
- Validate dữ liệu đầu vào (schema).
- Gọi core/processor để xử lý logic, sau đó lưu DB qua repository.
- Trả về phản hồi (status + message) rõ ràng, nhất quán cho client.
- Quản lý cấu hình môi trường và logging cho API.
- Cấu hình AI API (AI_API_URL/AI_API_KEY/AI_TIMEOUT) để gọi gợi ý hạ nhiệt.
- Phối hợp với core để trả kèm gợi ý AI trong response khi có cảnh báo.
- Test API bằng Postman/curl, ghi lại ví dụ request/response.
- Đảm bảo API chịu tải gửi liên tục (rate ổn định, không rớt request).
- Phạm vi chính: tầng API + core/processor, không thiết kế DB.

### Nguyễn Đình Chương - Data + Xử lý

- Thiết kế bảng DB, khóa chính/ngoại, index cơ bản.
- Viết models (ORM) và repository (CRUD/truy vấn).
- Xử lý tính toán trung bình, % tăng, cảnh báo.
- Thiết kế luồng xử lý (batch/stream) phù hợp.
- Chuẩn hóa thời gian, retry và logging cho phần xử lý dữ liệu.
- Chuẩn hóa dữ liệu đầu vào (range nhiệt độ hợp lệ, timestamp).
- Cung cấp dữ liệu cảnh báo cho UI theo format thống nhất.
- Phạm vi chính: data layer + core logic, không làm UI/firmware.

### Nguyễn Như Quỳnh - Desktop UI

- Thiết kế cửa sổ chính, layout dashboard và điều hướng màn hình.
- Lấy dữ liệu từ API (polling/timer) và xử lý hiển thị.
- Hiển thị nhiệt độ theo thời gian thực (bảng/biểu đồ).
- Hiển thị danh sách cảnh báo theo mức độ.
- Cung cấp màn hình cấu hình (ngưỡng, tần suất, URL API).
- Xử lý lỗi kết nối và trạng thái offline.
- Tối ưu UI để dễ dùng: màu cảnh báo, cập nhật mượt.
- Ghi lại hướng dẫn thao tác cơ bản cho người dùng.
- Phạm vi chính: UI desktop, không làm firmware/DB/schema.

## Checklist hiểu hệ thống (mỗi người tự xác nhận)

- [ ] Hiểu luồng dữ liệu từ thiết bị đến UI.
- [ ] Hiểu cấu trúc dự án và vai trò từng module.
- [ ] Hiểu logic cảnh báo và cách tính toán.
- [ ] Biết cách chạy API và UI ở máy cá nhân.
