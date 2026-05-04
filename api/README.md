# api/ - Flask server nhận dữ liệu

## Mục đích

Nhận dữ liệu từ thiết bị qua HTTP REST, kiểm tra payload, trả phản hồi.

## Chứa gì

- Điểm vào Flask app
- Định nghĩa route nhận dữ liệu
- Schema/validation payload

## Danh sách file

- **init**.py (package): Khai báo package, giúp import các module API.
- app.py (app factory): Tạo Flask app, nạp cấu hình, đăng ký routes/blueprint.
- routes.py (controller): Nhận request, gọi core/database, trả response JSON.
- schemas.py (schema/model): Định nghĩa schema request/response và validate payload.

## Ví dụ sử dụng

POST /api/temperature với JSON gồm sensor_id, temp, ts.
