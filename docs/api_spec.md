# Đặc tả API

## Authentication

- **POST /api/auth/register**: Đăng ký user mới
- **POST /api/auth/login**: Đăng nhập, trả về JWT
- **GET /api/auth/profile**: Lấy thông tin user

## Data

- **POST /api/du-lieu-nhiet**: Nhận dữ liệu nhiệt từ thiết bị
- **GET /api/du-lieu-nhiet**: Lấy danh sách dữ liệu gần nhất
- **GET /api/canh-bao**: Lấy danh sách cảnh báo

## AI

- **POST /api/ai/goi-y**: Lấy gợi ý từ AI

## Chi tiết Endpoints

### `POST /api/du-lieu-nhiet`

- **Mô tả**: Nhận dữ liệu nhiệt từ thiết bị.
- **Request Body**: `DuLieuNhietVao`
  ```json
  {
    "device_id": "sensor1",
    "temp": 32.5,
    "humidity": 65.0,
    "ts": "2026-06-17T12:00:00Z"
  }
  ```
- **Success Response (201 Created)**: `ApiResponse`
  ```json
  {
    "status": "success",
    "message": "Da nhan du lieu",
    "data": {
      "item": { /* DuLieuNhietRa */ },
      "alert": { /* AlertOut (nếu có) */ }
    }
  }
  ```
- **Error Response (422 Unprocessable Entity)**:
  ```json
  {
    "status": "error",
    "message": "Dữ liệu không hợp lệ",
    "errors": [ /* danh sách lỗi */ ]
  }
  ```

### `GET /api/du-lieu-nhiet`

- **Mô tả**: Lấy danh sách dữ liệu gần nhất.
- **Query Params**:
  - `device_id`: (bắt buộc)
  - `limit`: (mặc định 50)
- **Success Response (200 OK)**:
  ```json
  {
    "status": "success",
    "message": "OK",
    "data": {
      "items": [ /* list of DuLieuNhietRa */ ]
    }
  }
  ```

### `GET /api/canh-bao`

- **Mô tả**: Lấy danh sách cảnh báo gần nhất.
- **Query Params**:
  - `device_id`: (bắt buộc)
  - `limit`: (mặc định 50)
- **Success Response (200 OK)**:
  ```json
  {
    "status": "success",
    "message": "OK",
    "data": {
      "items": [ /* list of AlertOut */ ]
    }
  }
  ```

### `POST /api/ai/goi-y`

- **Mô tả**: Lấy gợi ý từ AI để giảm nhiệt độ.
- **Request Body**: `AiSuggestionRequest`
  ```json
  {
    "current_temp": 38.0,
    "avg_temp": 35.0,
    "threshold": 10.0
  }
  ```
- **Success Response (200 OK)**:
  ```json
  {
    "status": "success",
    "message": "OK",
    "data": {
      "suggestion": "Bật điều hòa, giảm nhiệt độ phòng."
    }
  }
  ```
---

## Pydantic Models (`schemas.py`)

- **`DuLieuNhietVao`**: Dữ liệu từ thiết bị (device_id, temp, humidity, ts)
- **`DuLieuNhietRa`**: Dữ liệu sau xử lý (thêm server_ts)
- **`AlertOut`**: Thông tin cảnh báo (avg_temp, percent_increase, level)
- **`ApiResponse`**: Phản hồi thành công (status, message, data)
- **`ErrorResponse`**: Phản hồi lỗi (status, message, errors)
- **`AiSuggestionRequest`**: Yêu cầu gợi ý AI
- **`AiSuggestionResponse`**: Phản hồi gợi ý AI
- **`UserLogin` / `UserRegister`**: Models cho authentication
- **`DeviceLink` / `DeviceSettings`**: Models cho quản lý thiết bị
