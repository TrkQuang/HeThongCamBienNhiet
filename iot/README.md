# iot/ - Thiết bị thật & hướng dẫn

## Mục đích

Chứa firmware và hướng dẫn cấu hình cho ESP8266/ESP32 + DHT11/DHT22.

## Chứa gì

- esp8266/: firmware cho ESP8266
- esp32/: firmware cho ESP32
- payload_check.py: script Python kiểm tra payload trước khi gửi

## Danh sách file

- esp8266/README.md (guide): Hướng dẫn cấu hình Wi-Fi, endpoint, chân DHT.
- esp8266/main.ino (firmware): Kết nối Wi-Fi, đọc DHT, tạo payload, gửi HTTP, retry.
- esp32/README.md (guide): Hướng dẫn cấu hình Wi-Fi, endpoint, chân DHT.
- esp32/main.ino (firmware): Kết nối Wi-Fi, đọc DHT, tạo payload, gửi HTTP, retry.
- payload_check.py (python): Kiểm tra format payload và giá trị đầu vào.

## Ví dụ sử dụng

Cấu hình Wi-Fi + URL API trong firmware, rồi upload qua Arduino IDE/PlatformIO.
Kiểm tra payload trước khi gửi bằng lệnh: `python iot/payload_check.py`.
