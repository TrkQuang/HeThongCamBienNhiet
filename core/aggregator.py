# core/aggregator.py
# tinh_trung_binh(), xu_ly_canh_bao()
from typing import List, Tuple
from .alert_rules import kiem_tra_canh_bao

def tinh_trung_binh(readings: List[float]) -> float:
    if not readings:
        return 0.0
    return sum(readings) / len(readings)

def xu_ly_canh_bao(readings: List[float], current_temp: float) -> Tuple[bool, float, str]:
    """Tính avg và kiểm tra cảnh báo đồng bộ."""
    avg = tinh_trung_binh(readings)
    canh_bao, percent_final, level = kiem_tra_canh_bao(avg, current_temp)
    return canh_bao, percent_final, level