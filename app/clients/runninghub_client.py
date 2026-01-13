from __future__ import annotations

from typing import Any, Optional
from urllib.parse import urlparse

import httpx

from app.config import get_settings


def normalize_runninghub_token(value: str) -> str:
    raw = str(value or "").strip()
    return raw.removeprefix("Bearer ").removeprefix("bearer ").strip()


def normalize_runninghub_base_url(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("RUNNINGHUB_BASE_URL is required")

    parsed = urlparse(raw)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("RUNNINGHUB_BASE_URL must use http(s)")
    if not parsed.netloc:
        raise ValueError("RUNNINGHUB_BASE_URL must include host")

    return raw.rstrip("/")


def build_image_to_video_realistic_payload(
    *,
    prompt: str,
    resolution: str,
    aspect_ratio: str,
    image_url: str,
    duration: int | str,
) -> dict[str, Any]:
    return {
        "prompt": prompt,
        "resolution": resolution,
        "aspectRatio": aspect_ratio,
        "imageUrl": image_url,
        "duration": str(duration),
    }


def extract_first_result_url(response_json: Any) -> str | None:
    if not isinstance(response_json, dict):
        return None

    results = response_json.get("results")
    if not isinstance(results, list) or not results:
        return None

    first = results[0]
    if not isinstance(first, dict):
        return None

    url = first.get("url")
    if isinstance(url, str) and url.strip():
        return url.strip()

    return None


class RunningHubClient:
    def __init__(
        self,
        *,
        token: str,
        base_url: Optional[str] = None,
        timeout_s: Optional[float] = None,
    ) -> None:
        settings = get_settings()
        self._base_url = normalize_runninghub_base_url(base_url or settings.RUNNINGHUB_BASE_URL)
        self._token = normalize_runninghub_token(token)

        if not self._token:
            raise ValueError("RUNNINGHUB token is required")

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout_s or settings.REQUEST_TIMEOUT,
            headers={"Authorization": f"Bearer {self._token}"},
        )

    async def image_to_video_realistic(
        self,
        *,
        prompt: str,
        resolution: str,
        aspect_ratio: str,
        image_url: str,
        duration: int | str,
    ) -> dict[str, Any]:
        payload = build_image_to_video_realistic_payload(
            prompt=prompt,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            image_url=image_url,
            duration=duration,
        )
        response = await self._client.post(
            "/openapi/v2/rhart-video-s-official/image-to-video-realistic",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "RunningHubClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

