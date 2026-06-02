# utils/time_sync.py
from datetime import datetime, timezone
import ntplib #là thư viện Python dùng để lấy thời gian chính xác từ server NTP (Network Time Protocol).

def lay_thoi_gian_utc() -> datetime:
    """Lấy thời gian UTC chuẩn từ NTP hoặc fallback local."""
    try:
        client = ntplib.NTPClient()
        response = client.request("pool.ntp.org", version=3, timeout=2)
        return datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
    except:
        return datetime.now(timezone.utc)
