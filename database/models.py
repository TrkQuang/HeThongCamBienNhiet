# database/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime
from .db import Base

class Reading(Base):
    __tablename__ = "DuLieuNhiet"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, index=True)
    device_id = Column(String, index=True)
    nhiet_do = Column(Float)
    do_am = Column(Float, nullable=True)
    thoi_gian_thiet_bi = Column(DateTime)
    thoi_gian_server = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_sensor_time', 'sensor_id', 'thoi_gian_server'),
    )

class Alert(Base):
    __tablename__ = "CanhBao"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, index=True)
    nhiet_do_tb = Column(Float)
    nhiet_do_hien_tai = Column(Float)
    phan_tram_tang = Column(Float)
    nguong = Column(Float)
    muc_do = Column(String)
    tao_luc = Column(DateTime, default=datetime.utcnow)