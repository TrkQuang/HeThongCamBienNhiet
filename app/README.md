# app/ - Giao diện desktop

## Mục đích

Hiển thị dữ liệu nhiệt độ theo thời gian thực, trạng thái cảm biến, cảnh báo.

## Chứa gì

- Điều phối UI (điểm vào)
- Cửa sổ chính và các màn hình chính
- Thành phần UI dùng lại

## Danh sách file

- **init**.py (package): Khai báo package, giúp import các module UI.
- main.py (entrypoint): Điểm chạy UI, nạp cấu hình, khởi tạo cửa sổ chính và event loop.
- main_window.py (view/controller): Định nghĩa cửa sổ chính, layout tổng và điều phối các view con.
- dashboard_view.py (view): Hiển thị dữ liệu realtime (bảng/biểu đồ).
- alert_panel.py (view): Hiển thị danh sách cảnh báo, trạng thái mức độ.
- settings_view.py (view): Form cấu hình ngưỡng, tần suất, URL API.
- widgets.py (ui components): Các widget dùng chung (card, badge, bảng).

## Ví dụ sử dụng

Chạy UI bằng lệnh: `python -m app.main`.
