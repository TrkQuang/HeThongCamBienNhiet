# Detail_Task.md - Phân công theo file

## Nguyên tắc

- Mỗi file có 1 người phụ trách chính.
- Người phụ trách chính chịu trách nhiệm cập nhật, chỉnh sửa và bàn giao.
- Các thành viên khác có thể góp ý qua review.
- Một số file có “phụ trách phụ” để phối hợp (Member 2 <-> Member 3).

## Nguyễn Phúc Tài - IoT (thiết bị)

- iot/README.md
- iot/esp8266/README.md
- iot/esp8266/main.ino
- iot/esp32/README.md
- iot/esp32/main.ino
- iot/payload_check.py

## Trần Kỳ Quang - API Flask

- requirements.txt
- api/**init**.py
- api/app.py
- api/routes.py
- api/schemas.py
- config/env.example
- config/logging.yaml
- core/processor.py
- core/**init**.py
- utils/validators.py

## Nguyễn Đình Chương - Data + Xử lý

- database/**init**.py
- database/db.py
- database/models.py
- database/repository.py
- core/aggregator.py
- core/alert_rules.py
- core/thresholds.py
- core/ai_suggester.py
- utils/**init**.py
- utils/time_sync.py
- utils/retry.py
- utils/logger.py
- utils/ai_client.py
- config/settings.yaml

## Nguyễn Như Quỳnh - Desktop UI

- app/**init**.py
- app/main.py
- app/main_window.py
- app/dashboard_view.py
- app/alert_panel.py
- app/settings_view.py
- app/widgets.py
