# database/repository.py
# LỆNH QUAN TRỌNG: save_reading(), get_recent_readings(), save_alert(), get_alerts()
# Đồng bộ với API: dùng cam_bien_id=sensor_id, thiet_bi_id=device_id, nhiet_do=temp
from sqlalchemy.orm import Session
from .models import Reading, Alert
from datetime import datetime
from typing import List, Optional

def save_reading(db: Session, sensor_id: str, device_id: str, temp: float, humidity: Optional[float], device_ts: Optional[datetime]) -> Reading:
    reading = Reading(
        sensor_id=sensor_id,
        device_id=device_id,
        nhiet_do=temp,
        do_am=humidity,
        thoi_gian_thiet_bi=device_ts
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading

def get_recent_readings(db: Session, sensor_id: Optional[str] = None, limit: int = 100) -> List[Reading]:
    q = db.query(Reading)
    if sensor_id:
        q = q.filter(Reading.sensor_id == sensor_id)
    return q.order_by(Reading.thoi_gian_server.desc()).limit(limit).all()

def save_alert(db: Session, sensor_id: str, avg_temp: float, current_temp: float,
               percent: float, threshold: float, level: str) -> Alert:
    alert = Alert(
        sensor_id=sensor_id,
        nhiet_do_tb=avg_temp,
        nhiet_do_hien_tai=current_temp,
        phan_tram_tang=percent,
        nguong=threshold,
        muc_do=level
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

def get_alerts(db: Session, sensor_id: Optional[str] = None, limit: int = 50) -> List[Alert]:
    q = db.query(Alert)
    if sensor_id:
        q = q.filter(Alert.sensor_id == sensor_id)
    return q.order_by(Alert.tao_luc.desc()).limit(limit).all()
