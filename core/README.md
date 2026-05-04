# core/ - Xử lý logic & cảnh báo

## Mục đích

Tính toán trung bình, % tăng, xác định cảnh báo và chuẩn hóa dữ liệu.

## Chứa gì

- Gom/đệm dữ liệu
- Quy tắc cảnh báo
- Xử lý theo lô hoặc thời gian thực

## Danh sách file

- **init**.py: Khai báo package, hỗ trợ import.
- processor.py: Điều phối luồng xử lý dữ liệu.
- aggregator.py: Gom dữ liệu và tính trung bình.
- alert_rules.py: Quy tắc cảnh báo theo % tăng.
- thresholds.py: Ngưỡng cảnh báo và cấu hình liên quan.

## Ví dụ sử dụng

Gọi `processor.process(readings)` để trả ra danh sách cảnh báo.
