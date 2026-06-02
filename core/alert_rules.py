# core/alert_rules.py
#  kiem_tra_canh_bao() - logic > 10%
from .thresholds import NGUONG_CANH_BAO

def kiem_tra_canh_bao(avg_temp: float, current_temp: float) -> tuple[bool, float, str]:
    """Trả về (có_cảnh_báo, percent, level)"""
    if avg_temp <= 0:
        return False, 0.0, ""
    percent = (current_temp - avg_temp) / avg_temp * 100
    if percent > NGUONG_CANH_BAO:
        level = "high" if percent > 20 else "warning"
        return True, percent, level
    return False, percent, ""
