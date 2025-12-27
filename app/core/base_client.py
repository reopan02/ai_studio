from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.models.schemas import TaskStatus


class BaseVideoClient(ABC):
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key
        self.base_url = self._normalize_base_url(base_url or settings.API_BASE_URL)
        self.client = httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        """
        Normalize and validate API base_url.

        Requirements:
        - Must include scheme and host
        - Must use HTTPS
        - Trailing slash is removed to avoid double-slash when joining with endpoint paths
        """
        value = str(base_url or "").strip()
        if not value:
            raise ValueError("base_url 不能为空")

        parsed = urlparse(value)
        if parsed.scheme.lower() != "https":
            raise ValueError("base_url 必须使用 HTTPS 协议")
        if not parsed.netloc:
            raise ValueError("base_url 必须包含 host，例如 https://api.example.com")

        return value.rstrip("/")

    def _build_url(self, endpoint: str) -> str:
        """
        Join `base_url` and endpoint path safely.

        - `endpoint` should be an absolute path like `/v2/...`
        - Ensures exactly one slash between base_url and endpoint
        """
        ep = str(endpoint or "").strip()
        if not ep:
            raise ValueError("endpoint 不能为空")
        if not ep.startswith("/"):
            ep = "/" + ep
        return f"{self.base_url}{ep}"

    @abstractmethod
    async def create_video(
        self,
        prompt: str,
        image: Optional[str] = None,
        **kwargs,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def query_task(self, task_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def parse_status(self, response: Dict[str, Any]) -> TaskStatus:
        raise NotImplementedError

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        settings = get_settings()
        url = self._build_url(endpoint)

        retrying = AsyncRetrying(
            stop=stop_after_attempt(settings.MAX_RETRIES),
            wait=wait_exponential(multiplier=settings.RETRY_BACKOFF_FACTOR),
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
            reraise=True,
        )

        async for attempt in retrying:
            with attempt:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()

        raise RuntimeError("Unreachable")

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
