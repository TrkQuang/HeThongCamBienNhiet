# database/__init__.py
from .db import get_db, init_db, Base
from .models import Reading, Alert
from .repository import (
    save_reading, get_recent_readings,
    save_alert, get_alerts
)
