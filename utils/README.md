# utils/ - Tiện ích dùng chung

## Mục đích

Tập hợp các hàm hỗ trợ: đồng bộ thời gian, retry, logging, validate.

## Chứa gì

- time_sync.py
- retry.py
- logger.py
- validators.py

## Danh sách file

- **init**.py: Khai báo package, hỗ trợ import.
- time_sync.py: Chuẩn hóa và đồng bộ timestamp.
- retry.py: Cơ chế retry/backoff khi lỗi tạm thời.
- logger.py: Cấu hình logging dùng chung.
- validators.py: Kiểm tra dữ liệu đầu vào.

## Ví dụ sử dụng

Dùng `utils.time_sync` để chuẩn hóa timestamp trước khi lưu DB.
