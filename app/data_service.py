import threading
import time
from typing import Any, Callable, Dict, List, Optional

from firebase.client import get_db
from firebase.device_repo import get_user_devices

from .api_client import ApiClient
from .ai_service import generate_suggestions
from .settings_store import AppSettings


LOI_AI = {
    "DANGER": "Nguy hiểm! Kiểm tra nguồn nhiệt ngay.",
    "WARNING": "Cảnh báo ngưỡng. Kiểm tra làm mát.",
}

# ── constants ──────────────────────────────────────────────────────────
_AI_DEBOUNCE = 5.0       # seconds between AI calls
_UI_THROTTLE = 0.2       # max ~5 fps for data-driven UI updates
_FETCH_COOLDOWN = 1.0    # minimum interval between fetch cycles


class DataService:
    def __init__(self, api_client: ApiClient, settings: AppSettings):
        self._api = api_client
        self._settings = settings
        self._device_id = settings.device_id

        # ── public state ───────────────────────────────────────────────
        self.current_data: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.ai_suggestion: Optional[str] = None
        self.ai_loading: bool = False
        self.ai_error: Optional[str] = None
        self.last_update = 0.0
        self.last_alert_write = 0.0
        self.measure_status: Optional[str] = None

        # ── internals ──────────────────────────────────────────────────
        self._subscribers: List[Callable[[], None]] = []
        self._lock = threading.Lock()
        self._data_listener = None
        self._settings_listener = None
        self._devices_listener = None
        self._alerts_listener = None

        # AI debounce & cache
        self._last_ai_call = 0.0
        self._ai_cache: Dict[str, str] = {}
        # UI refresh version — bumped on force_refresh so views reset tracking
        self._refresh_version = 0
        self._last_ui_update = 0.0
        # Device-list change detection
        self._last_device_ids: str = ""

        self._listen_user_devices()
        self._update_device_list()
        if self._device_id:
            self._restart_listeners()
            self.refresh_all()

    # ── public API ─────────────────────────────────────────────────────

    def subscribe(self, callback: Callable[[], None]) -> None:
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def _notify(self, force: bool = False) -> None:
        """Notify UI subscribers.

        *force=True* bypasses the throttle — use for AI results / alerts.
        *force=False* drops redundant notifications within *UI_THROTTLE* window.
        """
        if not force:
            now = time.time()
            if now - self._last_ui_update < _UI_THROTTLE:
                return
            self._last_ui_update = now
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
        self.force_refresh()

    def get_status(self, temp: float, do_am: float) -> str:
        if temp >= self._settings.danger_threshold:
            return "DANGER"
        if temp >= self._settings.warning_threshold or do_am >= self._settings.humidity_threshold:
            return "WARNING"
        return "NORMAL"

    def refresh_all(self, force: bool = False):
        if not force and time.time() - self.last_update < _FETCH_COOLDOWN:
            return
        self.last_update = 0  # reset cooldown so this fetch always runs
        threading.Thread(target=self._fetch_sync, daemon=True).start()

    def force_refresh(self):
        """Force a full refresh — reset UI tracking & AI cache so all views re-render."""
        self._ai_cache.clear()
        self._refresh_version += 1
        self.last_update = 0
        self.refresh_all(force=True)

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

    # ── listeners ──────────────────────────────────────────────────────

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
            self._alerts_listener = db.reference(f"alerts/{self._device_id}").listen(
                lambda _event: self._fetch_alerts_only()
            )
        except Exception as loi:
            print(f"[LISTENER] error: {loi}")

    def _listen_user_devices(self):
        try:
            db = get_db()
            if self._devices_listener is None:
                self._devices_listener = db.reference("users/default_user/devices").listen(
                    lambda _event: self._update_device_list()
                )
        except Exception as e:
            print(f"[LISTENER] user devices error: {e}")

    def _update_device_list(self):
        try:
            devices = get_user_devices("default_user")
            if not devices:
                return
            entries = [
                {"id": d.get("device_id", d.get("id")), "name": d.get("name", d.get("device_id", ""))}
                for d in devices
            ]
            # Skip if device list didn't actually change (avoids sidebar rebuild)
            sig = "|".join(sorted(f'{e["id"]}:{e["name"]}' for e in entries))
            if sig == self._last_device_ids:
                return
            self._last_device_ids = sig

            self._settings.devices = entries
            self._notify(force=True)  # device list change → force
        except Exception as e:
            print(f"[LISTENER] update devices error: {e}")

    def _fetch_alerts_only(self):
        if not self._device_id:
            return
        try:
            self.alerts = self._api.get_alerts(self._device_id, limit=15)
            self._notify(force=True)
        except Exception as e:
            print(f"[FETCH] alerts-only error: {e}")

    # ── alert persistence (debounced 30s) ───────────────────────────────

    def _check_and_write_alert(self, temp: float, status: str):
        if not self._device_id:
            return
        now = time.time()
        if now - self.last_alert_write < 30.0:
            return
        try:
            from firebase.alert_repo import save_alert
            from datetime import datetime, timezone, timedelta
            vn_tz = timezone(timedelta(hours=7))
            now_vn = datetime.now(vn_tz)
            alert_data = {
                "device_id": self._device_id,
                "temperature": temp,
                "temp": temp,
                "level": status,
                "warning": "Nguy hiểm! Kiểm tra nguồn nhiệt ngay." if status == "DANGER" else "Cảnh báo ngưỡng. Kiểm tra làm mát.",
                "timestamp": now_vn.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            save_alert(self._device_id, alert_data)
            self.last_alert_write = now
            print(f"[ALERT] wrote {status} alert for {self._device_id} temp={temp}")
        except Exception as e:
            print(f"[ALERT] write error: {e}")

    # ── main fetch cycle ───────────────────────────────────────────────

    def _fetch_sync(self):
        """Background thread: fetch data, THEN trigger AI separately."""
        if not self._device_id:
            return

        status = "NORMAL"
        nhiet_do = 0.0
        do_am = 0.0

        with self._lock:
            try:
                print(f"[FETCH] starting for device_id={self._device_id}")
                remote = self._api.get_settings(self._device_id)
                self._apply_settings(remote)

                self.history = self._api.get_sensor_history(self._device_id, limit=30)
                print(f"[FETCH] history: {len(self.history)} records")
                if self.history:
                    self.current_data = self.history[0]
                    nhiet_do = float(self.current_data.get("temp", 0))
                    do_am = float(self.current_data.get("humidity", 0))
                    status = self.get_status(nhiet_do, do_am)

                    if status in ("DANGER", "WARNING"):
                        self._check_and_write_alert(nhiet_do, status)

                self.alerts = self._api.get_alerts(self._device_id, limit=15)
                self.last_update = time.time()
            except Exception as loi:
                print(f"[FETCH] Fetch error: {loi}")
                return

        # ── AFTER lock: notify UI & trigger AI ─────────────────────────
        self._notify(force=False)  # sensor data update (throttled)

        if self.history:
            self._request_ai_suggestions(nhiet_do, do_am, status)

    # ── AI call: debounced + cached + thread-safe ─────────────────────

    def _request_ai_suggestions(self, nhiet_do: float, do_am: float, status: str):
        now = time.time()
        self.ai_error = None

        # NORMAL → use static text, skip AI
        if status == "NORMAL":
            self.ai_suggestion = self._gen_ai_text(status)
            self.ai_loading = False
            self._notify(force=True)
            return

        # Debounce: don't call more than once per _AI_DEBOUNCE
        if now - self._last_ai_call < _AI_DEBOUNCE:
            print(f"[AI] skipped — debounce ({now - self._last_ai_call:.1f}s < {_AI_DEBOUNCE}s)")
            return

        # Cache check: keyed by status + temp (rounded) + humidity
        cache_key = f"{status}_{nhiet_do:.1f}_{do_am:.0f}"
        cached = self._ai_cache.get(cache_key)
        if cached:
            print("[AI] cached result used")
            self.ai_suggestion = cached
            self.ai_loading = False
            self._notify(force=True)
            return

        # Fresh call — spawn background thread
        print("[AI] calling...")
        self.ai_loading = True
        self._notify(force=True)  # show "Đang tạo gợi ý..."
        threading.Thread(
            target=self._do_ai_call,
            args=(cache_key, status),
            daemon=True,
        ).start()

    def _do_ai_call(self, cache_key: str, status: str):
        """Run AI generation in background thread."""
        try:
            ctx = {
                "device_id": self._device_id,
                "sensor_data": self.current_data,
                "alerts": self.alerts,
                "status": status,
                "warning_threshold": self._settings.warning_threshold,
                "danger_threshold": self._settings.danger_threshold,
            }
            dynamic_sugg = generate_suggestions(ctx)
            if dynamic_sugg:
                self.ai_suggestion = dynamic_sugg
                self._ai_cache[cache_key] = dynamic_sugg
                self.ai_error = None
                print("[AI] finished — result from API")
            else:
                self.ai_suggestion = self._gen_ai_text(status)
                self.ai_error = "AI không phản hồi — đã dùng gợi ý mặc định"
                print("[AI] finished — empty response, used fallback")
        except Exception as e:
            self.ai_suggestion = self._gen_ai_text(status)
            self.ai_error = f"Lỗi AI: {e}"
            print(f"[AI] finished — error: {e}")
        finally:
            self.ai_loading = False
            self._last_ai_call = time.time()
            self._notify(force=True)  # AI result → force

    # ── helpers ─────────────────────────────────────────────────────────

    def _apply_settings(self, data: Dict[str, Any]):
        if not data:
            return
        old_warn = self._settings.warning_threshold
        old_danger = self._settings.danger_threshold

        self._settings.warning_threshold = float(
            data.get("temperatureThreshold", self._settings.warning_threshold)
        )
        self._settings.humidity_threshold = float(
            data.get("humidityThreshold", self._settings.humidity_threshold)
        )

        # Only overwrite danger_threshold if remote explicitly provides a valid (>0) value.
        # Otherwise keep the local setting — the API may not persist dangerThreshold.
        remote_danger = data.get("dangerThreshold")
        if remote_danger is not None:
            rd = float(remote_danger)
            if rd > 0:
                self._settings.danger_threshold = rd
            else:
                # Remote returned 0 (never saved) → keep local, fallback to warn+5
                if self._settings.danger_threshold <= 0:
                    self._settings.danger_threshold = self._settings.warning_threshold + 5.0
        else:
            # Key missing entirely → keep local value
            if self._settings.danger_threshold <= 0:
                self._settings.danger_threshold = self._settings.warning_threshold + 5.0

        print(f"[SETTINGS] WARNING: {self._settings.warning_threshold} | DANGER: {self._settings.danger_threshold} | remote_danger: {remote_danger}")

    @staticmethod
    def _gen_ai_text(status: str) -> str:
        return LOI_AI.get(status, "Hệ thống ổn định.")
