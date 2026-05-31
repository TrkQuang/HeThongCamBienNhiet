import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .routes import router


def _cau_hinh_logging() -> None:
	"""Cấu hình logging, ưu tiên file YAML nếu có PyYAML."""
	duong_dan = os.getenv("LOG_CONFIG", "config/logging.yaml")  # Đường dẫn cấu hình log
	try:
		import yaml
		from logging.config import dictConfig

		with open(duong_dan, "r", encoding="utf-8") as tep:
			dictConfig(yaml.safe_load(tep))  # Nạp cấu hình log từ YAML
	except Exception:
		muc = os.getenv("LOG_LEVEL", "INFO")
		logging.basicConfig(level=muc)  # Fallback khi thiếu PyYAML hoặc file log


def create_app() -> FastAPI:
	"""Tạo và cấu hình FastAPI app."""
	load_dotenv()  # Đọc biến môi trường từ .env nếu có
	_cau_hinh_logging()

	ung_dung = FastAPI(title="HeThongCamBienNhiet API")
	ung_dung.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_methods=["*"],
		allow_headers=["*"],
	)

	ung_dung.include_router(router)
	return ung_dung


app = create_app()


if __name__ == "__main__":
	dia_chi = os.getenv("API_HOST", "0.0.0.0")
	cong = int(os.getenv("API_PORT", "5000"))
	che_do_debug = os.getenv("API_DEBUG", "true").lower() == "true"
	uvicorn.run("api.app:app", host=dia_chi, port=cong, reload=che_do_debug)
