# database/ - Lưu trữ dữ liệu

## Mục đích

Quản lý kết nối DB và định nghĩa models cho dữ liệu nhiệt, cảnh báo.

## Chứa gì

- Kết nối DB (SQLite mặc định)
- Models dữ liệu
- Lớp repository thao tác đọc/ghi

## Danh sách file

- **init**.py (package): Khai báo package, giúp import các module DB.
- db.py (infrastructure): Tạo engine/session, cấu hình kết nối DB.
- models.py (model/ORM): Định nghĩa bảng dữ liệu (du_lieu_nhiet, canh_bao).
- repository.py (repository/service): CRUD và truy vấn theo sensor_id, thời gian.

## Ví dụ sử dụng

Khởi tạo kết nối trong `db.py`, sau đó gọi repository để lưu dữ liệu.
