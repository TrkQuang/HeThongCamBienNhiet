# database/db.py
# LỆNH QUAN TRỌNG NHẤT (Nguyễn Đình Chương):
# - init_db()          : tạo bảng khi chạy lần đầu
# - get_db()           : lấy session đồng bộ cho API/UI
# - DATABASE_URL       : cấu hình DB (mặc định sqlite)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///temperature.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
