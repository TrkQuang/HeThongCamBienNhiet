# Table.md - Danh sách bảng dữ liệu

## Mục tiêu

Liệt kê các bảng cần tạo cho hệ thống giám sát nhiệt độ đa điểm.

## 1) Bảng `DuLieuNhiet` (Reading)

Dữ liệu nhiệt độ theo thời gian.

| Cột                | Kiểu dữ liệu | Mô tả                         |
| ------------------ | ------------ | ----------------------------- |
| id                 | INTEGER (PK) | Khóa chính bản ghi            |
| sensor_id          | TEXT         | Mã cảm biến                   |
| device_id          | TEXT         | Mã thiết bị                   |
| nhiet_do           | REAL         | Nhiệt độ đo được              |
| do_am              | REAL         | Độ ẩm (nếu có)                |
| thoi_gian_thiet_bi | DATETIME     | Timestamp từ thiết bị         |
| thoi_gian_server   | DATETIME     | Timestamp ghi nhận tại server |

Index: sensor_id + thoi_gian_server

## 2) Bảng `CanhBao` (Alert)

Bảng lưu cảnh báo theo quy tắc % tăng.

| Cột               | Kiểu dữ liệu | Mô tả                       |
| ----------------- | ------------ | --------------------------- |
| id                | INTEGER (PK) | Khóa chính cảnh báo         |
| sensor_id         | TEXT         | Mã cảm biến                 |
| nhiet_do_tb       | REAL         | Nhiệt độ trung bình         |
| nhiet_do_hien_tai | REAL         | Nhiệt độ hiện tại           |
| phan_tram_tang    | REAL         | % tăng so với trung bình    |
| nguong            | REAL         | Ngưỡng cảnh báo             |
| muc_do            | TEXT         | Mức cảnh báo (warning/high) |
| tao_luc           | DATETIME     | Thời điểm tạo cảnh báo      |

## Ghi chú

- Bảng `DuLieuNhiet` có thể rất lớn: nên tạo index cho `sensor_id` và `thoi_gian_server`.
- Có thể bỏ `do_am` nếu chỉ đo nhiệt độ.
