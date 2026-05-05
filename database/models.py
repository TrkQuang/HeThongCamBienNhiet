# database/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_code = Column(String, unique=True, index=True)
    device_type = Column(String)
    firmware_version = Column(String)
    last_seen_at = Column(DateTime)

    # Quan hệ 1-N: 1 Thiết bị có nhiều Cảm biến
    sensors = relationship("Sensor", back_populates="device")

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    sensor_code = Column(String, unique=True, index=True)
    name = Column(String)
    location = Column(String)
    device_id = Column(Integer, ForeignKey("devices.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # các mối quan hệ
    device = relationship("Device", back_populates="sensors")
    readings = relationship("Reading", back_populates="sensor")
    alerts = relationship("Alert", back_populates="sensor")

class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), index=True) #index cho sensor_id để tối ưu truy vấn theo cảm biến
    temperature = Column(Float)
    humidity = Column(Float, nullable=True) # Có thể null nếu chỉ đo nhiệt độ
    device_ts = Column(DateTime)
    server_ts = Column(DateTime, default=datetime.utcnow, index=True) #index cho server_ts để tối ưu truy vấn theo thời gian

    sensor = relationship("Sensor", back_populates="readings")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    avg_temp = Column(Float)
    current_temp = Column(Float)
    percent_increase = Column(Float)
    threshold = Column(Float)
    level = Column(String) # VD: 'warning', 'high'
    created_at = Column(DateTime, default=datetime.utcnow)

    sensor = relationship("Sensor", back_populates="alerts")