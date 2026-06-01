from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
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

    def get_status(self) -> Dict[str, Any]:
        resp = self._session.get(self._url("/api/trang-thai"), timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    def get_readings(self, sensor_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if sensor_id:
            params["sensor_id"] = sensor_id

        resp = self._session.get(self._url("/api/du-lieu-nhiet"), params=params, timeout=self._timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("items", [])

    def get_alerts(self, sensor_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if sensor_id:
            params["sensor_id"] = sensor_id

        resp = self._session.get(self._url("/api/canh-bao"), params=params, timeout=self._timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("items", [])
