# Hướng dẫn sử dụng

## Cài đặt

1. **Clone project**:
   ```bash
   git clone <repository_url>
   cd HeThongCamBienNhiet
   ```

2. **Tạo môi trường ảo**:
   ```bash
   python -m venv venv
   # Windows
   venv\\Scripts\\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Cài đặt dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Cấu hình

1. **Firebase**:
   - Tạo service account trên Firebase Console.
   - Download file JSON credentials.
   - Sửa file `config/settings.yaml` với đường dẫn credentials và database URL.

2. **Thiết bị**:
   - Mở file `devices.json`
   - Cấu hình `device_id` mặc định và danh sách `devices`.
   - Thiết lập ngưỡng nhiệt độ (`warning_threshold`, `danger_threshold`).

## Chạy ứng dụng

1. **Chạy API Backend**:
   - Mở terminal thứ nhất.
   - Chạy lệnh:
     ```bash
     python -m api.app
     ```
   - API sẽ chạy tại `http://127.0.0.1:5000`

2. **Chạy UI Desktop**:
   - Mở terminal thứ hai.
   - Chạy lệnh:
     ```bash
     python -m app.main
     ```
   - Giao diện desktop sẽ khởi động và kết nối đến API.

## Sử dụng giao diện

### Dashboard
- **Thẻ thiết bị**: Hiển thị nhiệt độ/độ ẩm hiện tại của mỗi cảm biến.
- **Biểu đồ**: Trực quan hóa xu hướng nhiệt độ theo thời gian.
- **Trạng thái**: "Connected" nếu API hoạt động, "Disconnected" nếu có lỗi.

### Alert Panel
- Hiển thị danh sách các cảnh báo nhiệt độ vượt ngưỡng.
- Mỗi cảnh báo bao gồm: thời gian, thiết bị, nhiệt độ, mức độ (Warning/Danger).

### Settings
- **Refresh rate**: Tần suất cập nhật dữ liệu từ API (mili-giây).
- **Sound Alert**: Bật/tắt âm thanh cảnh báo.
- **Thresholds**:
  - `Warning Threshold (°C)`: Ngưỡng cảnh báo màu vàng.
  - `Danger Threshold (°C)`: Ngưỡng cảnh báo màu đỏ.
- **API URL**: Địa chỉ của backend API.
- **Save**: Lưu các thay đổi cấu hình vào file `devices.json`.
