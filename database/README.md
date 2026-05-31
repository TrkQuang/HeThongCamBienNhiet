# database/ - Lưu trữ dữ liệu (Nguyễn Đình Chương)

## Mục đích
Cung cấp layer database đồng bộ: models + repository cho API/UI lấy dữ liệu.

## Chứa gì
- Kết nối DB (SQLite mặc định)
- Models chuẩn theo Table.md (DuLieuNhiet, CanhBao)
- Repository CRUD + truy vấn đồng bộ

## Danh sách file
- __init__.py: Export models & functions
- db.py: Engine, SessionLocal, init_db, get_db
- models.py: Reading (DuLieuNhiet), Alert (CanhBao)
- repository.py: save_reading, get_recent_readings, save_alert, get_alerts
- Table.md: Schema bảng dữ liệu

## Sử dụng đồng bộ (cho API/UI)
```python
from database import get_db, save_reading, get_recent_readings, save_alert, get_alerts
db = next(get_db())
reading = save_reading(db, sensor_id="S01", device_id="D01", temp=28.5, humidity=60, device_ts=...)
alerts = get_alerts(db, sensor_id="S01")
```