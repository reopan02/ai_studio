from __future__ import annotations

from typing import Any, Iterable, Optional
from urllib.parse import urlparse

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings


class ImageEditsClient:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key
        self.base_url = self._normalize_base_url(base_url or settings.IMAGE_EDIT_API_BASE_URL)
        self.client = httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
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
        ep = str(endpoint or "").strip()
        if not ep:
            raise ValueError("endpoint 不能为空")
        if not ep.startswith("/"):
            ep = "/" + ep
        return f"{self.base_url}{ep}"

    async def images_generations(
        self,
        *,
        model: str,
        prompt: str,
        n: int = 1,
        size: str | None = None,
        response_format: str | None = None,
    ) -> Any:
        """Text-to-image generation following OpenAI DALL-E format.

        Note: Some upstream providers reject the `n` parameter. Callers SHOULD
        perform batching/concurrency themselves and this client will not send
        `n` upstream.
        """
        endpoint = "/v1/images/generations"
        url = self._build_url(endpoint)

        payload: dict[str, Any] = {"model": model, "prompt": prompt}
        if size:
            payload["size"] = size
        if response_format:
            payload["response_format"] = response_format

        settings = get_settings()
        retrying = AsyncRetrying(
            stop=stop_after_attempt(settings.MAX_RETRIES),
            wait=wait_exponential(multiplier=settings.RETRY_BACKOFF_FACTOR),
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
            reraise=True,
        )

        async for attempt in retrying:
            with attempt:
                response = await self.client.post(url, json=payload)
                response.raise_for_status()
                return response.json()

        raise RuntimeError("Unreachable")

    async def images_edits(
        self,
        *,
        model: str,
        prompt: str,
        response_format: str | None = None,
        aspect_ratio: str | None = None,
        image_size: str | None = None,
        images: Iterable[tuple[str, bytes, str]] | None = None,
    ) -> Any:
        endpoint = "/v1/images/edits"
        url = self._build_url(endpoint)

        data: dict[str, str] = {"model": model, "prompt": prompt}
        if response_format:
            data["response_format"] = response_format
        if aspect_ratio:
            data["aspect_ratio"] = aspect_ratio
        if image_size:
            data["image_size"] = image_size

        files: list[tuple[str, tuple[str, bytes, str]]] = []
        if images:
            for filename, content, content_type in images:
                files.append(("image", (filename, content, content_type)))

        settings = get_settings()
        retrying = AsyncRetrying(
            stop=stop_after_attempt(settings.MAX_RETRIES),
            wait=wait_exponential(multiplier=settings.RETRY_BACKOFF_FACTOR),
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
            reraise=True,
        )

        async for attempt in retrying:
            with attempt:
                response = await self.client.post(url, data=data, files=files)
                response.raise_for_status()
                return response.json()

        raise RuntimeError("Unreachable")

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

