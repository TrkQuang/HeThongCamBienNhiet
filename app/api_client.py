from __future__ import annotations

from typing import Any, Dict, List, Optional
import requests

class ApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()

    @property
    def base_url(self) -> str:
        return self._base_url

    def update_base_url(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def _payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Hỗ trợ cả 2 kiểu response: data và du_lieu."""
        if not isinstance(data, dict):
            return {}
        payload = data.get("du_lieu")
        if payload is None:
            payload = data.get("data")
        return payload if isinstance(payload, dict) else {}

    # Devices
    def get_device(self, device_id: str) -> Dict[str, Any]:
        resp = self._session.get(self._url(f"/api/devices/{device_id}"), timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    # Sensors
    def get_sensor_latest(self, device_id: str) -> Dict[str, Any]:
        resp = self._session.get(self._url(f"/api/sensor/latest/{device_id}"), timeout=self._timeout)
        resp.raise_for_status()
        data = resp.json()
        print("\n[DEBUG] response sensor latest:", data)
        return data

    def get_sensor_history(self, device_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        resp = self._session.get(
            self._url("/api/du-lieu-nhiet"),
            params={"device_id": device_id, "limit": limit},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        print("\n[DEBUG] response sensor history:", data)
        payload = self._payload(data)
        return payload.get("items", [])

    # Settings
    def get_settings(self, device_id: str) -> Dict[str, Any]:
        resp = self._session.get(self._url(f"/api/settings/{device_id}"), timeout=self._timeout)
        resp.raise_for_status()
        data = resp.json()
        print("\n[DEBUG] response settings:", data)
        return data

    def update_settings(self, device_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._session.put(
            self._url(f"/api/settings/{device_id}"),
            json=settings,
            timeout=self._timeout
        )
        resp.raise_for_status()
        return resp.json()

    # Alerts
    def get_alerts(self, device_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        params = {"limit": limit}
        if device_id:
            params["device_id"] = device_id
        # Sử dụng endpoint đồng bộ với backend đã sửa
        resp = self._session.get(
            self._url("/api/alerts"),
            params=params,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        print("\n[DEBUG] response alerts:", data)
        payload = self._payload(data)
        return payload.get("items", [])

    # AI Suggestions
    def get_ai_suggestions(self, nhiet_do_hien_tai: float, nhiet_do_trung_binh: float, nguong: float) -> Optional[str]:
        payload = {
            "nhiet_do_hien_tai": nhiet_do_hien_tai,
            "nhiet_do_trung_binh": nhiet_do_trung_binh,
            "nguong": nguong,
        }
        resp = self._session.post(
            self._url("/api/ai/goi-y"),
            json=payload,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        print("response ai suggestions:", data)
        payload_data = self._payload(data)
        suggestion = payload_data.get("suggestion")
        return str(suggestion) if suggestion is not None else None
