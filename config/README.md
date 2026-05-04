# config/ - Cấu hình hệ thống

## Mục đích

Tách cấu hình khỏi code để dễ chỉnh theo môi trường.

## Chứa gì

- settings.yaml
- logging.yaml
- env.example

## Danh sách file

- settings.yaml (config): Ngưỡng cảnh báo, tần suất gửi/nhận, URL API, DB path.
- logging.yaml (config): Mức log, format, nơi ghi log.
- env.example (env template): Mẫu biến môi trường cần thiết.

## Ví dụ sử dụng

Cập nhật `settings.yaml` để đổi ngưỡng cảnh báo hoặc URL API.
