from __future__ import annotations
from typing import Any, Dict, List, Optional
import requests

class ApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()

    def update_base_url(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    def _url(self, path: str):
        return f"{self._base_url}{path}"

    @staticmethod
    def _payload(resp: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(resp, dict): return {}
        return resp.get("du_lieu") or resp.get("data") or {}

    def get_device(self, device_id: str) -> Dict[str, Any]:
        raw = self._get(f"/api/devices/{device_id}")
        # API wraps response in {"ok": True, "data": {...}, "message": "OK"}
        # Unwrap to get the inner payload (which has {exists, device_id})
        return self._payload(raw)

    def get_devices(self) -> List[Dict[str, Any]]:
        """Fetch all linked devices from API."""
        return self._items(self._get("/api/devices"))

    def get_sensor_history(self, device_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return self._items(self._get("/api/du-lieu-nhiet", {"device_id": device_id, "limit": limit}))

    def get_settings(self, device_id: str) -> Dict[str, Any]:
        return self._get(f"/api/settings/{device_id}")

    def update_settings(self, device_id: str, cai_dat: Dict[str, Any]) -> Dict[str, Any]:
        return self._put(f"/api/settings/{device_id}", cai_dat)

    def get_alerts(self, device_id: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if device_id: params["device_id"] = device_id
        return self._items(self._get("/api/alerts", params))

    def get_ai_suggestions(self, nhiet_do_hien_tai: float, nhiet_do_trung_binh: float, nguong: float) -> Optional[str]:
        payload = {"nhiet_do_hien_tai": nhiet_do_hien_tai, "nhiet_do_trung_binh": nhiet_do_trung_binh, "nguong": nguong}
        suggestion = self._payload(self._post("/api/ai/goi-y", payload)).get("suggestion")
        return str(suggestion) if suggestion is not None else None

    def _get(self, path: str, params: Any = None) -> Dict[str, Any]:
        resp = self._session.get(self._url(path), params=params, timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._session.post(self._url(path), json=payload, timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    def _put(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._session.put(self._url(path), json=payload, timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    def _items(self, resp: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._payload(resp).get("items", [])