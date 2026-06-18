import threading
import time
from typing import Any, Callable, Dict, List, Optional

from firebase.client import get_db

from .api_client import ApiClient
from .settings_store import AppSettings


LOI_AI = {
    "DANGER": "Nguy hiểm! Kiểm tra nguồn nhiệt ngay.",
    "WARNING": "Cảnh báo ngưỡng. Kiểm tra làm mát.",
}


class DataService:
    def __init__(self, api_client: ApiClient, settings: AppSettings):
        self._api = api_client
        self._settings = settings
        self._device_id = settings.device_id

        self.current_data: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.ai_suggestion: Optional[str] = None
        self.last_update = 0.0
        self.measure_status: Optional[str] = None

        self._subscribers: List[Callable[[], None]] = []
        self._lock = threading.Lock()
        self._data_listener = None
        self._settings_listener = None

        if self._device_id:
            self._restart_listeners()
            self.refresh_all()

    def subscribe(self, callback: Callable[[], None]) -> None:
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def _notify(self):
        for cb in self._subscribers:
            try:
                cb()
            except Exception as loi:
                print(f"Notify error: {loi}")

    def update_settings(self, settings: AppSettings):
        cu = self._device_id
        self._settings = settings
        self._device_id = settings.device_id
        self._api.update_base_url(settings.api_base_url)

        if cu != self._device_id:
            self._restart_listeners()
        self.refresh_all()

    def _restart_listeners(self):
        if not self._device_id:
            return

        try:
            db = get_db()
            self._data_listener = db.reference(f"sensor_data/{self._device_id}").listen(
                lambda _event: self.refresh_all()
            )
            self._settings_listener = db.reference(f"settings/{self._device_id}").listen(
                lambda _event: self.refresh_all()
            )
        except Exception as loi:
            print(f"Listener error: {loi}")

    def get_status(self, temp: float, do_am: float) -> str:
        if temp >= self._settings.danger_threshold:
            return "DANGER"
        if temp >= self._settings.warning_threshold or do_am >= self._settings.humidity_threshold:
            return "WARNING"
        return "NORMAL"

    def refresh_all(self):
        if time.time() - self.last_update < 1.0:
            return
        threading.Thread(target=self._fetch_sync, daemon=True).start()

    def _fetch_sync(self):
        if not self._device_id:
            return

        with self._lock:
            try:
                remote = self._api.get_settings(self._device_id)
                self._apply_settings(remote)

                self.history = self._api.get_sensor_history(self._device_id, limit=30)
                if self.history:
                    self.current_data = self.history[0]
                    nhiet_do = float(self.current_data.get("temp", 0))
                    do_am = float(self.current_data.get("humidity", 0))
                    self.ai_suggestion = self._gen_ai_text(self.get_status(nhiet_do, do_am))

                self.alerts = self._api.get_alerts(self._device_id, limit=15)
                self.last_update = time.time()
                self._notify()
            except Exception as loi:
                print(f"Fetch error: {loi}")

    def _apply_settings(self, data: Dict[str, Any]):
        if not data:
            return

        self._settings.warning_threshold = float(
            data.get("temperatureThreshold", self._settings.warning_threshold)
        )
        self._settings.humidity_threshold = float(
            data.get("humidityThreshold", self._settings.humidity_threshold)
        )
        self._settings.danger_threshold = self._settings.warning_threshold + 5.0

    @staticmethod
    def _gen_ai_text(status: str) -> str:
        return LOI_AI.get(status, "Hệ thống ổn định.")

    def request_immediate_measure(self):
        try:
            get_db().reference(f"settings/{self._device_id}/forceMeasure").set(1)
            self.measure_status = "pending"
        except Exception:
            self.measure_status = "timeout"

    @property
    def device_id(self) -> Optional[str]:
        return self._device_id

    @property
    def settings(self) -> AppSettings:
        return self._settings