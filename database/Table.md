# Table.md - Danh sách bảng dữ liệu

## Mục tiêu

Liệt kê các bảng cần tạo cho hệ thống giám sát nhiệt độ đa điểm.

## 1) Bảng `sensors`

Thông tin cảm biến/điểm đo.

| Cột         | Kiểu dữ liệu | Mô tả                  |
| ----------- | ------------ | ---------------------- |
| id          | INTEGER (PK) | Khóa chính cảm biến    |
| sensor_code | TEXT         | Mã cảm biến (duy nhất) |
| name        | TEXT         | Tên cảm biến           |
| location    | TEXT         | Vị trí lắp đặt         |
| device_id   | INTEGER (FK) | Tham chiếu thiết bị    |
| created_at  | DATETIME     | Thời điểm tạo          |

## 2) Bảng `devices`

Thông tin thiết bị IoT (ESP8266/ESP32).

| Cột              | Kiểu dữ liệu | Mô tả                         |
| ---------------- | ------------ | ----------------------------- |
| id               | INTEGER (PK) | Khóa chính thiết bị           |
| device_code      | TEXT         | Mã thiết bị (duy nhất)        |
| device_type      | TEXT         | Loại thiết bị (ESP8266/ESP32) |
| firmware_version | TEXT         | Phiên bản firmware            |
| last_seen_at     | DATETIME     | Lần cuối thiết bị gửi dữ liệu |

## 3) Bảng `readings`

Dữ liệu nhiệt độ theo thời gian.

| Cột         | Kiểu dữ liệu | Mô tả                         |
| ----------- | ------------ | ----------------------------- |
| id          | INTEGER (PK) | Khóa chính bản ghi            |
| sensor_id   | INTEGER (FK) | Tham chiếu cảm biến           |
| temperature | REAL         | Nhiệt độ đo được              |
| humidity    | REAL         | Độ ẩm (nếu có)                |
| device_ts   | DATETIME     | Timestamp từ thiết bị         |
| server_ts   | DATETIME     | Timestamp ghi nhận tại server |

## 4) Bảng `alerts`

Bảng lưu cảnh báo theo quy tắc % tăng.

| Cột              | Kiểu dữ liệu | Mô tả                       |
| ---------------- | ------------ | --------------------------- |
| id               | INTEGER (PK) | Khóa chính cảnh báo         |
| sensor_id        | INTEGER (FK) | Tham chiếu cảm biến         |
| avg_temp         | REAL         | Nhiệt độ trung bình         |
| current_temp     | REAL         | Nhiệt độ hiện tại           |
| percent_increase | REAL         | % tăng so với trung bình    |
| threshold        | REAL         | Ngưỡng cảnh báo             |
| level            | TEXT         | Mức cảnh báo (warning/high) |
| created_at       | DATETIME     | Thời điểm tạo cảnh báo      |

## Ghi chú

- Bảng `readings` có thể rất lớn: nên tạo index cho `sensor_id` và `server_ts`.
- Có thể bỏ `humidity` nếu chỉ đo nhiệt độ.
- Có thể gộp `devices` vào `sensors` nếu hệ thống đơn giản.
