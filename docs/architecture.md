# Kiến trúc Hệ thống Giám sát Nhiệt độ

## Tổng quan

Hệ thống giám sát nhiệt độ đa điểm với kiến trúc 3 tầng:

```
┌─────────────────┐
│  ESP8266/ESP32  │
│  (Thiết bị IoT) │
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────────────────────────┐
│         API Backend (FastAPI)       │
│  - Nhận dữ liệu nhiệt độ           │
│  - Tính toán % tăng                │
│  - Tạo cảnh báo nếu vượt ngưỡng    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    Firebase Realtime Database       │
│  - sensors/{device_id}/data        │
│  - alerts/{timestamp}              │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    Desktop UI (Tkinter)            │
│  - Dashboard realtime              │
│  - Alert panel                     │
│  - Settings                        │
└─────────────────────────────────────┘
```

## Các thành phần chính

### 1. API Backend (`api/`)

**Công nghệ**: FastAPI + Uvicorn

**Các module**:
- `app.py`: Factory tạo FastAPI app, cấu hình CORS, logging
- `routes.py`: Router chính xử lý dữ liệu nhiệt độ
- `auth_routes.py`: Router xác thực người dùng
- `device_routes.py`: Router quản lý thiết bị
- `settings_routes.py`: Router cấu hình hệ thống
- `schemas.py`: Pydantic models cho request/response

**Chức năng**:
- Nhận dữ liệu nhiệt độ từ thiết bị ESP qua HTTP POST
- Validate payload bằng Pydantic
- Tính % tăng nhiệt độ so với trung bình (100 readings gần nhất)
- Tạo cảnh báo nếu % tăng > ngưỡng (mặc định 10%)
- Lưu dữ liệu vào Firebase
- Cung cấp API gợi ý AI để giảm nhiệt

### 2. Firebase Layer (`firebase/`)

**Công nghệ**: firebase-admin SDK

**Cấu trúc dữ liệu**:
```
firebase/
├── sensor_repo.py      # sensors/{device_id}/data
├── alert_repo.py       # alerts/{device_id}/{timestamp}
├── device_repo.py      # devices/{device_id}
├── user_repo.py        # users/{username}
└── settings_repo.py    # settings/{device_id}
```

**Cấu hình**:
- Credentials: `config/settings.yaml` hoặc biến môi trường
- Database URL: `FIREBASE_DATABASE_URL`

### 3. Desktop UI (`app/`)

**Công nghệ**: Tkinter

**Các màn hình**:
- **Dashboard** (`dashboard_view_modern.py`):
  - Hiển thị nhiệt độ realtime
  - Biểu đồ xu hướng
  - Thẻ thiết bị
  
- **Alert Panel** (`alert_panel.py`):
  - Danh sách cảnh báo
  - Màu sắc theo mức độ (xanh/vàng/đỏ)
  - Thời gian cảnh báo
  
- **Settings** (`settings_view.py`):
  - Ngưỡng nhiệt độ (warning/danger)
  - Tần suất cập nhật
  - Bật/tắt âm thanh

**Quản lý dữ liệu**:
- `data_service.py`: Lấy dữ liệu từ API
- `api_client.py`: HTTP client giao tiếp với backend
- `settings_store.py`: Lưu cấu hình local (JSON)

## Luồng dữ liệu

### 1. Thiết bị gửi dữ liệu

```python
# ESP gửi
POST /api/du-lieu-nhiet
{
  "device_id": "sensor1",
  "temp": 32.5,
  "humidity": 65.0,
  "ts": "2026-06-17T12:00:00Z"
}
```

### 2. API xử lý

1. **Validate payload** bằng Pydantic schema
2. **Lưu vào Firebase**: `sensors/{device_id}/data`
3. **Tính toán**:
   - Lấy 100 readings gần nhất
   - Tính trung bình: `trung_binh = sum(temps) / len(temps)`
   - Tính % tăng: `percent = (current - avg) / avg * 100`
4. **Kiểm tra ngưỡng**:
   - Nếu `percent > 10%` → tạo cảnh báo
   - Xác định mức độ: warning/danger
5. **Lưu cảnh báo** vào Firebase nếu vượt ngưỡng

### 3. UI hiển thị

- Polling API mỗi 3 giây (cấu hình được)
- Cập nhật dashboard realtime
- Hiển thị popup cảnh báo nếu có alert mới
- Phát âm thanh nếu `sound_alert = True`

## Logic cảnh báo

```python
# Tính toán
trung_binh = sum(nhiet_do_list) / len(nhiet_do_list)
percent_tang = (nhiet_do_hien_tai - trung_binh) / trung_binh * 100

# Xác định mức độ
if percent_tang > NGUONG_CANH_BAO:  # mặc định 10%
    if nhiet_do_hien_tai > danger_threshold:  # mặc định 40°C
        muc_do = "danger"
    else:
        muc_do = "warning"
    # Tạo cảnh báo
```

## Cấu hình

### Biến môi trường

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `API_HOST` | Host API | `0.0.0.0` |
| `API_PORT` | Port API | `5000` |
| `API_DEBUG` | Chế độ debug | `true` |
| `FIREBASE_CREDENTIALS` | Đường dẫn credentials | - |
| `FIREBASE_DATABASE_URL` | Firebase database URL | - |

### File cấu hình

**`config/settings.yaml`**:
```yaml
firebase:
  credentials_path: "../iot/key_firebase_HeThongNhiet.json"
  database_url: "https://hethongcambiennhiet-default-rtdb.asia-southeast1.firebasedatabase.app/"

api:
  host: "127.0.0.1"
  port: 5000
```

**`devices.json`** (local settings):
```json
{
  "api_base_url": "http://127.0.0.1:5000",
  "device_id": "sensor1",
  "devices": [
    {"id": "sensor1", "name": "Phòng khách"}
  ],
  "warning_threshold": 35.0,
  "danger_threshold": 40.0,
  "refresh_ms": 3000,
  "sound_alert": true
}
```

## Bảo mật

- **Xác thực**: JWT token (auth_routes.py)
- **CORS**: Cho phép tất cả origins (development)
- **Firebase**: Service account credentials

## Mở rộng

- **MQTT**: Thay HTTP cho IoT protocol
- **AI dự báo**: Machine learning dự đoán xu hướng nhiệt
- **Multi-user**: Phân quyền theo người dùng
- **Mobile app**: React Native/Flutter
