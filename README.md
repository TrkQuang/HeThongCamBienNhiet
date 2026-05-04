# Ứng dụng desktop giám sát và cảnh báo nhiệt độ đa điểm (IoT + Python)

## Mục tiêu

- Nhận dữ liệu nhiệt độ thời gian thực từ ESP8266/ESP32 qua HTTP.
- Hiển thị trên desktop và cảnh báo khi vượt ngưỡng.

## Tổng quan cấu trúc

- app/: Giao diện desktop (Tkinter/PyQt)
- api/: Flask REST API
- core/: Xử lý logic, tính toán, cảnh báo
- database/: Kết nối DB và models
- iot/: Firmware + hướng dẫn thiết bị
- data/: Dữ liệu/DB cục bộ
- utils/: Helper dùng chung
- config/: Cấu hình hệ thống
- docs/: Tài liệu

## Luồng dữ liệu

Thiết bị -> API -> Core -> DB -> UI

## Logic hệ thống

- Trung bình: trung_binh = tong_nhiet_do / so_luong
- % tăng: phan_tram_tang = (nhiet_do_hien_tai - trung_binh) / trung_binh * 100
- Nếu phan_tram_tang > 10 -> cảnh báo

## Cách chạy nhanh (gợi ý)

1. Tạo môi trường ảo và cài đặt `requirements.txt`.
2. Chạy API: `python -m api.app`
3. Chạy UI: `python -m app.main`

## Mở rộng ( nếu còn thời gian )

- MQTT thay HTTP
- AI dự báo xu hướng
