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
        
        self._db_ref = None
        self._listener = None
        
        # Initial data load and listener setup
        if self._device_id:
            self._restart_listener()
            self.refresh_all()

    def subscribe(self, callback: Callable):
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            # Send current data immediately if available
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

    def update_settings(self, settings: AppSettings):
        """Called when settings or active device changes."""
        old_device_id = self._device_id
        self._settings = settings
        self._device_id = settings.device_id
        self._api_client.update_base_url(settings.api_base_url)
        
        if old_device_id != self._device_id:
            print(f"[DataService] Switching device to: {self._device_id}")
            self._restart_listener()
            self.refresh_all()
        else:
            # If only thresholds changed, we might want to refresh AI suggestions
            self.refresh_all()

    def _restart_listener(self):
        if self._listener:
            try:
                self._listener.close()
                print("[DataService] Closed old listener")
            except Exception as e:
                print(f"[DataService] Error closing listener: {e}")
        
        if not self._device_id:
            return

        try:
            db = get_db()
            # Listener on the readings path
            self._db_ref = db.reference(f"iot/dht11_data/{self._device_id}")
            
            def listener_callback(event):
                # event.data could be a single push or the whole node
                # We trigger a refresh whenever anything changes
                print(f"[DataService] Realtime update detected for {self._device_id}")
                self.refresh_all()
                
            self._listener = self._db_ref.listen(listener_callback)
            print(f"[DataService] Started listener for {self._device_id}")
        except Exception as e:
            print(f"[DataService] Firebase listener error: {e}")

    def refresh_all(self):
        """Triggers a full data fetch in a separate thread."""
        # Debounce rapid updates
        now = time.time()
        if now - self.last_update < 1.0: # Minimum 1s between refreshes
            return
            
        threading.Thread(target=self._fetch_sync, daemon=True).start()

    def _fetch_sync(self):
        if not self._device_id:
            return

        with self._lock:
            try:
                # 1. Fetch History & Latest Data
                # We fetch a bit more for history to calculate AI suggestions and charts
                readings = self._api_client.get_sensor_history(self._device_id, limit=30)
                self.history = readings
                if readings:
                    self.current_data = readings[0]
                
                # 2. Fetch Alerts
                self.alerts = self._api_client.get_alerts(self._device_id, limit=15)
                
                # 3. Fetch AI Suggestion
                if readings:
                    valid_temps = [float(item["temp"]) for item in readings if item.get("temp") is not None]
                    if valid_temps:
                        avg_temp = sum(valid_temps) / len(valid_temps)
                        latest_temp = valid_temps[0]
                        threshold = self._settings.warning_threshold
                        
                        try:
                            self.ai_suggestion = self._api_client.get_ai_suggestions(
                                nhiet_do_hien_tai=latest_temp,
                                nhiet_do_trung_binh=avg_temp,
                                nguong=threshold
                            )
                        except Exception as ai_err:
                            print(f"[DataService] AI Suggester error: {ai_err}")
                
                self.last_update = time.time()
                print(f"[DataService] Data successfully synced for {self._device_id}")
                self._notify_subscribers()
            except Exception as e:
                print(f"[DataService] Fetch error: {e}")

    @property
    def device_id(self) -> Optional[str]:
        return self._device_id

    @property
    def settings(self) -> AppSettings:
        return self._settings