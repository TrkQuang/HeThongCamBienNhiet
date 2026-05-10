# Table.md - Danh sách bảng dữ liệu

## Mục tiêu

Liệt kê các bảng cần tạo cho hệ thống giám sát nhiệt độ đa điểm.

## 1) Bảng `cam_bien`

Thông tin cảm biến/điểm đo.

| Cột         | Kiểu dữ liệu | Mô tả                  |
| ----------- | ------------ | ---------------------- |
| id          | INTEGER (PK) | Khóa chính cảm biến    |
| ma_cam_bien | TEXT         | Mã cảm biến (duy nhất) |
| ten         | TEXT         | Tên cảm biến           |
| vi_tri      | TEXT         | Vị trí lắp đặt         |
| thiet_bi_id | INTEGER (FK) | Tham chiếu thiết bị    |
| tao_luc     | DATETIME     | Thời điểm tạo          |

## 2) Bảng `thiet_bi`

Thông tin thiết bị IoT (ESP8266/ESP32).

| Cột                | Kiểu dữ liệu | Mô tả                         |
| ------------------ | ------------ | ----------------------------- |
| id                 | INTEGER (PK) | Khóa chính thiết bị           |
| ma_thiet_bi        | TEXT         | Mã thiết bị (duy nhất)        |
| loai_thiet_bi      | TEXT         | Loại thiết bị (ESP8266/ESP32) |
| phien_ban_firmware | TEXT         | Phiên bản firmware            |
| lan_cuoi_thay      | DATETIME     | Lần cuối thiết bị gửi dữ liệu |

## 3) Bảng `du_lieu_nhiet`

Dữ liệu nhiệt độ theo thời gian.

| Cột                | Kiểu dữ liệu | Mô tả                         |
| ------------------ | ------------ | ----------------------------- |
| id                 | INTEGER (PK) | Khóa chính bản ghi            |
| cam_bien_id        | INTEGER (FK) | Tham chiếu cảm biến           |
| nhiet_do           | REAL         | Nhiệt độ đo được              |
| do_am              | REAL         | Độ ẩm (nếu có)                |
| thoi_gian_thiet_bi | DATETIME     | Timestamp từ thiết bị         |
| thoi_gian_server   | DATETIME     | Timestamp ghi nhận tại server |

## 4) Bảng `canh_bao`

Bảng lưu cảnh báo theo quy tắc % tăng.

| Cột               | Kiểu dữ liệu | Mô tả                       |
| ----------------- | ------------ | --------------------------- |
| id                | INTEGER (PK) | Khóa chính cảnh báo         |
| cam_bien_id       | INTEGER (FK) | Tham chiếu cảm biến         |
| nhiet_do_tb       | REAL         | Nhiệt độ trung bình         |
| nhiet_do_hien_tai | REAL         | Nhiệt độ hiện tại           |
| phan_tram_tang    | REAL         | % tăng so với trung bình    |
| nguong            | REAL         | Ngưỡng cảnh báo             |
| muc_do            | TEXT         | Mức cảnh báo (warning/high) |
| tao_luc           | DATETIME     | Thời điểm tạo cảnh báo      |

## Ghi chú

- Bảng `du_lieu_nhiet` có thể rất lớn: nên tạo index cho `cam_bien_id` và `thoi_gian_server`.
- Có thể bỏ `do_am` nếu chỉ đo nhiệt độ.
- Có thể gộp `thiet_bi` vào `cam_bien` nếu hệ thống đơn giản.
