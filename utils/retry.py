# utils/retry.py
import time
from typing import Callable, Any

def retry(func: Callable, max_attempts: int = 3, delay: float = 1.0) -> Any:
    """Thực hiện lại hàm khi lỗi (sync)."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(delay * (attempt + 1))
    return None
