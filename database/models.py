# database/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class ThietBi(Base):
    __tablename__ = "thiet_bi"

    id_thiet_bi = Column(Integer, primary_key=True, index=True)
    ma_cam_bien = Column(String, unique=True, index=True)
    vi_tri = Column(String)
    nguong_nhiet_do = Column(Float, default=35.0)
    ngay_tao = Column(DateTime, default=datetime.utcnow)

    # Relationship để truy xuất dữ liệu liên kết dễ dàng hơn
    nhat_ky = relationship("NhatKyNhietDo", back_populates="thiet_bi")
    canh_bao = relationship("CanhBao", back_populates="thiet_bi")

class NhatKyNhietDo(Base):
    __tablename__ = "nhat_ky_nhiet_do"

    id_nhat_ky = Column(Integer, primary_key=True, index=True)
    id_thiet_bi = Column(Integer, ForeignKey("thiet_bi.id_thiet_bi"))
    nhiet_do = Column(Float)
    thoi_gian_do = Column(DateTime, default=datetime.utcnow, index=True) # Đã thêm index cho thời gian

    thiet_bi = relationship("ThietBi", back_populates="nhat_ky")

class CanhBao(Base):
    __tablename__ = "canh_bao"

    id_canh_bao = Column(Integer, primary_key=True, index=True)
    id_thiet_bi = Column(Integer, ForeignKey("thiet_bi.id_thiet_bi"))
    loai_canh_bao = Column(String)
    noi_dung = Column(String)
    thoi_gian_canh_bao = Column(DateTime, default=datetime.utcnow)

    thiet_bi = relationship("ThietBi", back_populates="canh_bao")