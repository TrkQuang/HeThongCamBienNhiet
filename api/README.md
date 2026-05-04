# api/ - Flask server nhận dữ liệu

## Mục đích

Nhận dữ liệu từ thiết bị qua HTTP REST, kiểm tra payload, trả phản hồi.

## Chứa gì

- Điểm vào Flask app
- Định nghĩa route nhận dữ liệu
- Schema/validation payload

## Danh sách file

- **init**.py: Khai báo package, hỗ trợ import.
- app.py: Tạo Flask app, cấu hình, đăng ký routes.
- routes.py: Định nghĩa endpoint nhận dữ liệu.
- schemas.py: Schema/validation payload.

## Ví dụ sử dụng

POST /api/temperature với JSON gồm sensor_id, temp, ts.
