# core/ - Xử lý logic & cảnh báo

## Mục đích

Tính toán trung bình, % tăng, xác định cảnh báo và chuẩn hóa dữ liệu.

## Chứa gì

- Gom/đệm dữ liệu
- Quy tắc cảnh báo
- Xử lý theo lô hoặc thời gian thực

## Danh sách file

- **init**.py (package): Khai báo package, giúp import các module xử lý.
- processor.py (service): Điều phối luồng xử lý, gọi aggregator và alert_rules.
- aggregator.py (service): Gom dữ liệu theo sensor, tính trung bình/rolling.
- alert_rules.py (rules/service): Áp dụng quy tắc % tăng để tạo cảnh báo.
- thresholds.py (config/domain): Ngưỡng mặc định và logic đọc cấu hình ngưỡng.
- ai_suggester.py (service): Gọi AI để gợi ý cách hạ nhiệt.

## Ví dụ sử dụng

Gọi `processor.process(readings)` để trả ra danh sách cảnh báo.
