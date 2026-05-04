# app/ - Giao diện desktop

## Mục đích

Hiển thị dữ liệu nhiệt độ theo thời gian thực, trạng thái cảm biến, cảnh báo.

## Chứa gì

- Điều phối UI (điểm vào)
- Cửa sổ chính và các màn hình chính
- Thành phần UI dùng lại

## Danh sách file

- **init**.py: Khai báo package, hỗ trợ import.
- main.py: Điểm vào UI, khởi tạo ứng dụng.
- main_window.py: Cửa sổ chính và layout tổng.
- dashboard_view.py: Màn hình dashboard hiển thị dữ liệu.
- alert_panel.py: Bảng/cửa sổ cảnh báo.
- settings_view.py: Màn hình cấu hình hệ thống.
- widgets.py: Các widget dùng chung.

## Ví dụ sử dụng

Chạy UI bằng lệnh: `python -m app.main`.
