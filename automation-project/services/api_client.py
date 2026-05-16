"""
Layer 4 — SERVICE: ApiClient
Base HTTP client wrapping requests.Session.
All domain services inherit or compose this client.
"""
import json
from typing import Optional
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class ApiClient:

    def __init__(self, base_url: str, headers: Optional[dict] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            **(headers or {}),
        })

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"GET {url}")
        return self.session.get(url, **kwargs)

    def post(self, endpoint: str, payload: dict = None, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"POST {url} | body={payload}")
        return self.session.post(url, json=payload, **kwargs)

    def put(self, endpoint: str, payload: dict = None, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.put(url, json=payload, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.delete(url, **kwargs)
