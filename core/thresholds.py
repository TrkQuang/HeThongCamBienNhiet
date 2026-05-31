# core/thresholds.py
from __future__ import annotations

import os
from pathlib import Path


def _doc_nguong() -> float:
	mac_dinh = 10.0
	gia_tri_env = os.getenv("ALERT_THRESHOLD_PERCENT")
	if gia_tri_env:
		try:
			return float(gia_tri_env)
		except ValueError:
			return mac_dinh

	duong_dan = Path("config/settings.yaml")
	if not duong_dan.is_file():
		return mac_dinh

	try:
		import yaml

		with duong_dan.open("r", encoding="utf-8") as tep:
			du_lieu = yaml.safe_load(tep) or {}
		nguong = du_lieu.get("alert", {}).get("threshold_percent", mac_dinh)
		return float(nguong)
	except Exception:
		return mac_dinh


NGUONG_CANH_BAO = _doc_nguong()  # % tăng so với trung bình
