# database/db.py
# - init_db()          : tạo bảng khi chạy lần đầu
# - get_db()           : lấy session đồng bộ cho API/UI
# - DATABASE_URL       : cấu hình DB (mặc định sqlite)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path


def _doc_db_url() -> str:
    gia_tri_env = os.getenv("DATABASE_URL")
    if gia_tri_env:
        return gia_tri_env

    duong_dan = Path("config/settings.yaml")
    if not duong_dan.is_file():
        return "sqlite:///temperature.db"

    try:
        import yaml

        with duong_dan.open("r", encoding="utf-8") as tep:
            du_lieu = yaml.safe_load(tep) or {}
        url = du_lieu.get("database", {}).get("url", "sqlite:///temperature.db")
        return str(url)
    except Exception:
        return "sqlite:///temperature.db"


DATABASE_URL = _doc_db_url()

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
