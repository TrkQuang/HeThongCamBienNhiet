import threading
import time
from typing import Dict, Any, List, Optional, Callable
from .api_client import ApiClient
from .settings_store import AppSettings
from firebase.client import get_db

class DataService:
    def __init__(self, api_client: ApiClient, settings: AppSettings):
        self._api_client = api_client
        self._settings = settings
        self._device_id = settings.device_id

        self.current_data: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.ai_suggestion: Optional[str] = None
        self.last_update: float = 0

        self._subscribers: List[Callable] = []
        self._lock = threading.Lock()

        self._data_ref = None
        self._settings_ref = None
        self._data_listener = None
        self._settings_listener = None

        # Initial load & listeners
        if self._device_id:
            self._restart_listener()
            self.refresh_all()

    # -----------------------------------------------------------------
    # Subscription handling
    # -----------------------------------------------------------------
    def subscribe(self, callback: Callable):
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            if self.current_data or self.alerts:
                callback()

    def unsubscribe(self, callback: Callable):
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _notify_subscribers(self):
        for cb in self._subscribers:
            try:
                cb()
            except Exception as e:
                print(f"[DataService] Error notifying subscriber: {e}")

    # -----------------------------------------------------------------
    # Settings update (device switch, threshold changes, etc.)
    # -----------------------------------------------------------------
    def update_settings(self, settings: AppSettings):
        old_device_id = self._device_id
        self._settings = settings
        self._device_id = settings.device_id
        self._api_client.update_base_url(settings.api_base_url)

        if old_device_id != self._device_id:
            print(f"[DataService] Switching device to: {self._device_id}")
            self._restart_listener()
            self.refresh_all()
        else:
            self.refresh_all()

    # -----------------------------------------------------------------
    # Firebase realtime listeners
    # -----------------------------------------------------------------
    def _restart_listener(self):
        for name in ("_data_listener", "_settings_listener"):
            listener = getattr(self, name, None)
            if listener:
                try:
                    listener.close()
                    print(f"[DataService] Closed old {name}")
                except Exception as e:
                    print(f"[DataService] Error closing {name}: {e}")
                setattr(self, name, None)

        if not self._device_id:
            return

        try:
            db = get_db()
            self._data_ref = db.reference(f"sensor_data/{self._device_id}")
            self._settings_ref = db.reference(f"settings/{self._device_id}")

            def data_cb(event):
                print(f"[DataService] Sensor realtime update detected for {self._device_id}")
                self.refresh_all()

            def settings_cb(event):
                print(f"[DataService] Settings realtime update detected for {self._device_id}")
                data = self._settings_ref.get() or {}
                self._apply_remote_settings(data)
                self._refresh_ai_suggestion()
                self._notify_subscribers()

            self._data_listener = self._data_ref.listen(data_cb)
            self._settings_listener = self._settings_ref.listen(settings_cb)
            print(f"[DataService] Started listeners for {self._device_id}")
        except Exception as e:
            print(f"[DataService] Firebase listener error: {e}")

    # -----------------------------------------------------------------
    # Public refresh entry point
    # -----------------------------------------------------------------
    def refresh_all(self):
        now = time.time()
        if now - self.last_update < 1.0:
            return
        threading.Thread(target=self._fetch_sync, daemon=True).start()

    # -----------------------------------------------------------------
    # Centralised status logic
    # -----------------------------------------------------------------
    def _determine_status(self, temp: float, humidity: float) -> str:
        if temp >= self._settings.danger_threshold:
            return "DANGER"
        if temp >= self._settings.warning_threshold:
            return "WARNING"
        if humidity >= self._settings.humidity_threshold:
            return "WARNING"
        return "NORMAL"

    def _build_ai_suggestion(self, status: str, temp: float, humidity: float) -> str:
        if status == "DANGER":
            return (
                "Nhiệt độ đang ở mức nguy hiểm. Có nguy cơ ảnh hưởng thiết bị. "
                "Cần xử lý ngay, kiểm tra nguồn nhiệt và hệ thống thông gió."
            )
        if status == "WARNING":
            return (
                "Nhiệt độ đã vượt ngưỡng cảnh báo hoặc độ ẩm vượt ngưỡng. "
                "Nên kiểm tra hệ thống làm mát và theo dõi nhiệt độ trong thời gian tới."
            )
        return "Nhiệt độ ổn định. Hệ thống hoạt động bình thường. Tiếp tục theo dõi."

    def _refresh_ai_suggestion(self) -> None:
        if not self.current_data:
            self.ai_suggestion = None
            return

        temp = float(self.current_data.get("temp", 0))
        humidity = float(self.current_data.get("humidity", 0))
        status = self._determine_status(temp, humidity)
        self.ai_suggestion = self._build_ai_suggestion(status, temp, humidity)

    # -----------------------------------------------------------------
    # Alert logging on status change
    # -----------------------------------------------------------------
    def _log_alert(self, status: str, reading: Dict[str, Any]) -> None:
        from firebase.alert_repo import save_alert
        # Fill required AlertOut fields with safe defaults.
        # avg_temp – use current temperature as a placeholder if not available.
        avg_temp = reading.get("temp")
        alert_payload = {
            "timestamp": reading.get("timestamp") or reading.get("ts"),
            "created_at_unix": int(time.time()),
            "avg_temp": float(avg_temp) if avg_temp is not None else 0.0,
            "temp": reading.get("temp"),
            "percent_increase": 0.0,
            "threshold": float(self._settings.warning_threshold),
            "level": status,
            "warning": f"Nhiệt độ {status.lower()} mức ngưỡng",
        }
        try:
            save_alert(self._device_id, alert_payload)
        except Exception as e:
            print(f"[DataService] Alert log error: {e}")

    # -----------------------------------------------------------------
    # Core sync routine
    # -----------------------------------------------------------------
    def _fetch_sync(self):
        if not self._device_id:
            return

        with self._lock:
            try:
                # 0️⃣ sync settings from Firebase
                remote_settings = self._api_client.get_settings(self._device_id)
                self._apply_remote_settings(remote_settings)

                # 1️⃣ fetch sensor history
                readings = self._api_client.get_sensor_history(self._device_id, limit=30)
                self.history = readings

                previous_status = getattr(self, "_last_status", "UNKNOWN")
                current_status = "UNKNOWN"

                if readings:
                    self.current_data = readings[0]
                    temp = float(self.current_data.get("temp", 0))
                    hum = float(self.current_data.get("humidity", 0))
                    current_status = self._determine_status(temp, hum)
                    if current_status != previous_status:
                        self._log_alert(current_status, self.current_data)
                    self._last_status = current_status

                # 2️⃣ fetch alerts (already stored by _log_alert)
                self.alerts = self._api_client.get_alerts(self._device_id, limit=15)

                # 3️⃣ AI suggestion: use the same centralized status as Dashboard/Alert.
                self._refresh_ai_suggestion()

                self.last_update = time.time()
                print(f"[DataService] Data successfully synced for {self._device_id}")
                self._notify_subscribers()
            except Exception as e:
                print(f"[DataService] Fetch error: {e}")

    # -----------------------------------------------------------------
    # Apply remote settings (including danger threshold handling)
    # -----------------------------------------------------------------
    def _apply_remote_settings(self, data: Dict[str, Any]):
        if not isinstance(data, dict):
            return

        if data.get("temperatureThreshold") is not None:
            self._settings.warning_threshold = float(data["temperatureThreshold"])
        if data.get("humidityThreshold") is not None:
            self._settings.humidity_threshold = float(data["humidityThreshold"])
        if data.get("notificationEnabled") is not None:
            self._settings.sound_alert = bool(data["notificationEnabled"])
        if data.get("samplingInterval") is not None:
            minutes = max(int(data["samplingInterval"]), 1)
            self._settings.refresh_ms = minutes * 60000

        # danger temperature threshold – compute locally, do NOT push to backend
        # because the backend DeviceSettings model does not include this field.
        if data.get("dangerTemperatureThreshold") is not None:
            self._settings.danger_threshold = float(data["dangerTemperatureThreshold"])
        else:
            # default: warning + 5°C (local only)
            self._settings.danger_threshold = self._settings.warning_threshold + 5.0

    @property
    def device_id(self) -> Optional[str]:
        return self._device_id

    @property
    def settings(self) -> AppSettings:
        return self._settings