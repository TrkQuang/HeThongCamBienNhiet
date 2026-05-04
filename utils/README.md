# utils/ - Tiện ích dùng chung

## Mục đích

Tập hợp các hàm hỗ trợ: đồng bộ thời gian, retry, logging, validate.

## Chứa gì

- time_sync.py
- retry.py
- logger.py
- validators.py

## Danh sách file

- **init**.py (package): Khai báo package, giúp import các tiện ích.
- time_sync.py (utility): Chuẩn hóa timestamp, chuyển đổi timezone, kiểm tra lệch thời gian.
- retry.py (utility): Chính sách retry/backoff khi lỗi tạm thời.
- logger.py (utility/config): Cấu hình logger dùng chung, format và mức log.
- validators.py (utility/validation): Kiểm tra dữ liệu đầu vào, range và kiểu dữ liệu.

## Ví dụ sử dụng

Dùng `utils.time_sync` để chuẩn hóa timestamp trước khi lưu DB.
