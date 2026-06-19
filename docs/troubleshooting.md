# Xử lý sự cố

## 1. API không phản hồi
**Dấu hiệu**: UI hiển thị "Disconnected"
**Nguyên nhân**: 
- API chưa chạy hoặc bị crash
- Port 5000 bị chiếm dụng
**Khắc phục**:
```bash
# Kiểm tra port
netstat -ano | findstr :5000
# Đổi port trong config/settings.yaml
api:
  port: 5001
```

## 2. Lỗi Firebase connection
**Dấu hiệu**: `RuntimeError: Firebase settings are missing`
**Nguyên nhân**:
- Thiếu file credentials
- Sai database URL
**Khắc phục**:
1. Tạo service account trên Firebase Console
2. Sửa file `config/settings.yaml`:
```yaml
firebase:
  credentials_path: "C:/path/to/serviceAccountKey.json"
  database_url: "https://your-project.firebaseio.com"
```

## 3. Thiết bị không gửi dữ liệu
**Dấu hiệu**: Không có dữ liệu trên dashboard
**Nguyên nhân**:
- Payload ESP sai định dạng
- Device ID không khớp
**Kiểm tra**:
```python
# Payload đúng
{
  "device_id": "sensor1",
  "temp": 32.5,
  "ts": "2026-06-17T12:00:00Z"
}
```

## 4. Cảnh báo không xuất hiện
**Nguyên nhân**:
- Ngưỡng nhiệt độ cấu hình quá cao
- Thiếu tính % tăng nhiệt
**Sửa**:
- Mở `app/settings_store.py` → giảm `warning_threshold`
- Kiểm tra logic tính toán trong `api/routes.py` dòng 55-57

## 5. Lỗi đăng nhập (401 Unauthorized)
**Nguyên nhân**:
- Token JWT hết hạn
- Header Authorization thiếu
**Khắc phục**:
- Gửi lại request với header:
`Authorization: Bearer <token>`
- Đăng nhập lại để lấy token mới

## 6. Biểu đồ không cập nhật
**Nguyên nhân**:
- Tần suất refresh quá thấp
- Thiếu dữ liệu từ API
**Sửa**:
- Mở Settings → tăng `refresh_ms` (mặc định 3000ms)
- Kiểm tra API endpoint `/api/du-lieu-nhiet` có trả dữ liệu