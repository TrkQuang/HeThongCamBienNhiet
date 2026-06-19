import re
import os

# 1. Update firebase/sensor_repo.py
sensor_repo_path = "firebase/sensor_repo.py"
with open(sensor_repo_path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("iot/dht11_data", "sensor_data")
with open(sensor_repo_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated sensor_repo.py")

# 2. Update firebase/device_repo.py
device_repo_path = "firebase/device_repo.py"
with open(device_repo_path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("iot/dht11_data", "sensor_data")
with open(device_repo_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated device_repo.py")

# 3. Update api/schemas.py
schemas_path = "api/schemas.py"
with open(schemas_path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("measurement_interval_minutes: Optional[int]", "samplingInterval: Optional[int]")
with open(schemas_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated schemas.py")

# 4. Update app/main_window.py
main_window_path = "app/main_window.py"
with open(main_window_path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace(
    '"Settings": SettingsView(self.khung_view, self._settings, self._luu_cau_hinh)',
    '"Settings": SettingsView(self.khung_view, self._data_service, self._luu_cau_hinh)'
)
content = content.replace(
    '"measurement_interval_minutes": cau_hinh.measurement_interval_minutes',
    '"samplingInterval": cau_hinh.measurement_interval_minutes'
)
with open(main_window_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main_window.py")

# 5. Update iot/esp8266/main/main.ino
ino_path = "iot/esp8266/main/main.ino"
if os.path.exists(ino_path):
    with open(ino_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(
        'if (Firebase.getInt(fbdo, pathSetting + "/measurement_interval_minutes"))',
        'if (Firebase.getInt(fbdo, pathSetting + "/samplingInterval"))'
    )
    with open(ino_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated main.ino")

