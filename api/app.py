import logging
import os

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from .routes import nhom_api
from database.db import init_db


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


def create_app() -> Flask:
	"""Tạo và cấu hình Flask app."""
	load_dotenv()  # Đọc biến môi trường từ .env nếu có
	ung_dung = Flask(__name__)
	ung_dung.config["JSON_AS_ASCII"] = False  # Cho phép tiếng Việt có dấu trong JSON

	CORS(ung_dung)  # Cho phép gọi API từ UI desktop
	_cau_hinh_logging()
	init_db()  # Đảm bảo DB được khởi tạo trước khi nhận request
	ung_dung.register_blueprint(nhom_api)  # Đăng ký routes API
	return ung_dung


if __name__ == "__main__":
	ung_dung = create_app()
	dia_chi = os.getenv("API_HOST", "0.0.0.0")
	cong = int(os.getenv("API_PORT", "5000"))
	che_do_debug = os.getenv("API_DEBUG", "true").lower() == "true"
	ung_dung.run(host=dia_chi, port=cong, debug=che_do_debug)  # Chạy server cho môi trường phát triển
