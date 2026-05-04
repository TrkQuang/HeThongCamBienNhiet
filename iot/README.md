# iot/ - Thiết bị thật & hướng dẫn

## Mục đích

Chứa firmware và hướng dẫn cấu hình cho ESP8266/ESP32 + DHT11/DHT22.

## Chứa gì

- esp8266/: firmware cho ESP8266
- esp32/: firmware cho ESP32

## Danh sách file

- esp8266/README.md: Hướng dẫn cấu hình và nạp firmware ESP8266.
- esp8266/main.ino: Firmware ESP8266 đọc DHT, gửi dữ liệu HTTP.
- esp32/README.md: Hướng dẫn cấu hình và nạp firmware ESP32.
- esp32/main.ino: Firmware ESP32 đọc DHT, gửi dữ liệu HTTP.

## Ví dụ sử dụng

Cấu hình Wi-Fi + URL API trong firmware, rồi upload qua Arduino IDE/PlatformIO.
