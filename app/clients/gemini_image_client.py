from __future__ import annotations

import base64
from typing import Any, Iterable, Optional
from urllib.parse import urlparse

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings


class GeminiImageClient:
    """Client for Gemini image generation API (generateContent endpoint)."""

    # Models that use Gemini API format
    GEMINI_MODELS = {
        "gemini-3-pro-image-preview",
        "gemini-2.5-flash-image",
        "gemini-2.0-flash-exp",
    }

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key
        self.base_url = self._normalize_base_url(base_url or "https://yunwu.ai")
        self.client = httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        value = str(base_url or "").strip()
        if not value:
            raise ValueError("base_url 不能为空")

        parsed = urlparse(value)
        if parsed.scheme.lower() not in ("https", "http"):
            raise ValueError("base_url 必须使用 HTTP 或 HTTPS 协议")
        if not parsed.netloc:
            raise ValueError("base_url 必须包含 host，例如 https://api.example.com")

        return value.rstrip("/")

    @classmethod
    def is_gemini_model(cls, model: str) -> bool:
        """Check if the model should use Gemini API format."""
        return model in cls.GEMINI_MODELS or model.startswith("gemini-")

    def _build_url(self, model: str) -> str:
        """Build the generateContent URL for a model."""
        return f"{self.base_url}/v1beta/models/{model}:generateContent"

    async def generate_image(
        self,
        *,
        model: str,
        prompt: str,
        aspect_ratio: str | None = None,
        image_size: str | None = None,
        images: Iterable[tuple[str, bytes, str]] | None = None,
    ) -> dict[str, Any]:
        """
        Generate or edit images using Gemini API.

        Args:
            model: Model name (e.g., "gemini-3-pro-image-preview")
            prompt: Text prompt for generation/editing
            aspect_ratio: Aspect ratio (e.g., "16:9", "1:1")
            image_size: Image size for Gemini 3 Pro ("1K", "2K", "4K")
            images: Optional list of (filename, bytes, content_type) for editing

        Returns:
            Dict with generated image data in b64_json format
        """
        url = self._build_url(model)

        # Build parts array
        parts: list[dict[str, Any]] = []

        # Add reference images first (for editing)
        if images:
            for filename, content, content_type in images:
                # Convert bytes to base64
                b64_data = base64.b64encode(content).decode("utf-8")
                parts.append({
                    "inlineData": {
                        "mimeType": content_type,
                        "data": b64_data
                    }
                })

        # Add text prompt
        parts.append({"text": prompt})

        # Build request payload per API spec (banana.md)
        payload: dict[str, Any] = {
            "contents": [{
                "role": "user",
                "parts": parts
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
            }
        }

        # Add image config for aspect ratio and image size
        image_config: dict[str, Any] = {}
        if aspect_ratio:
            image_config["aspectRatio"] = aspect_ratio

        # Add image_size for Gemini 3 Pro (must be uppercase K)
        if image_size:
            # Ensure uppercase K
            normalized_size = image_size.upper().replace("K", "K")
            if normalized_size in ("2K", "4K"):
                image_config["imageSize"] = normalized_size

        if image_config:
            payload["generationConfig"]["imageConfig"] = image_config

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
                gemini_response = response.json()

                # Convert Gemini response to OpenAI-compatible format
                return self._convert_response(gemini_response)

        raise RuntimeError("Unreachable")

    def _convert_response(self, gemini_response: dict[str, Any]) -> dict[str, Any]:
        """Convert Gemini response to OpenAI-compatible format."""
        data: list[dict[str, Any]] = []

        candidates = gemini_response.get("candidates", [])
        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            for part in parts:
                # Handle inline image data
                if "inlineData" in part:
                    inline_data = part["inlineData"]
                    data.append({
                        "b64_json": inline_data.get("data", ""),
                        "revised_prompt": None
                    })
                # Also check for inline_data (snake_case)
                elif "inline_data" in part:
                    inline_data = part["inline_data"]
                    data.append({
                        "b64_json": inline_data.get("data", ""),
                        "revised_prompt": None
                    })

        # If no images found, return the raw response for debugging
        if not data:
            # Check if there's text response
            for candidate in candidates:
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if "text" in part:
                        # Return text as error message
                        return {
                            "error": {
                                "message": part["text"],
                                "type": "no_image_generated"
                            }
                        }

            return {
                "error": {
                    "message": "No image data in response",
                    "type": "no_image_generated",
                    "raw_response": gemini_response
                }
            }

        return {"data": data}

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
