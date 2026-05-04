# database/ - Lưu trữ dữ liệu

## Mục đích

Quản lý kết nối DB và định nghĩa models cho cảm biến, bản ghi, cảnh báo.

## Chứa gì

- Kết nối DB (SQLite mặc định)
- Models dữ liệu
- Lớp repository thao tác đọc/ghi

## Danh sách file

- **init**.py: Khai báo package, hỗ trợ import.
- db.py: Kết nối DB, tạo engine/session.
- models.py: Định nghĩa bảng (sensor, reading, alert).
- repository.py: Hàm CRUD và truy vấn dữ liệu.

## Ví dụ sử dụng

Khởi tạo kết nối trong `db.py`, sau đó gọi repository để lưu dữ liệu.
