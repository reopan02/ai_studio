import base64
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote
from urllib.parse import urlparse

from app.core.base_client import BaseVideoClient
from app.models.schemas import TaskStatus


class Sora2Client(BaseVideoClient):
    """
    OpenAI Sora (sora-2 / sora-2-pro) client.

    Endpoint conventions (HTTPS only):
    - Create generation: POST `{base_url}/v2/videos/generations`
    - Query status:     GET  `{base_url}/v2/videos/generations/{task_id}`
      - `task_id` is URL-encoded as a path segment (quote with safe="")
    """

    _GENERATIONS_PATH = "/v2/videos/generations"

    def _prepare_images(self, images: List[str]) -> List[str]:
        prepared: List[str] = []
        for img in images:
            value = (img or "").strip()
            if not value:
                raise ValueError("images 不能包含空字符串")

            if value.startswith("data:image"):
                prepared.append(value)
                continue

            parsed = urlparse(value)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                prepared.append(value)
                continue

            path = Path(value)
            if path.exists() and path.is_file():
                suffix = path.suffix.lower()
                mime_map = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".webp": "image/webp",
                    ".gif": "image/gif",
                }
                mime_type = mime_map.get(suffix, "image/jpeg")
                with open(path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                prepared.append(f"data:{mime_type};base64,{encoded}")
                continue

            raise ValueError(f"无法识别的图片格式: {value}")

        return prepared

    def _validate_request(
        self,
        *,
        prompt: str,
        model: str,
        aspect_ratio: str,
        duration: int,
        hd: bool,
        watermark: bool,
        private: bool,
        notify_hook: Optional[str],
        images: Optional[List[str]],
    ) -> None:
        if not prompt or not prompt.strip():
            raise ValueError("prompt 不能为空")

        if model not in {"sora-2", "sora-2-pro"}:
            raise ValueError("model 必须是 sora-2 或 sora-2-pro")

        if aspect_ratio not in {"16:9", "9:16"}:
            raise ValueError("aspect_ratio 必须是 16:9 或 9:16")

        if duration not in {10, 15, 25}:
            raise ValueError("duration 必须是 10 / 15 / 25")

        if model == "sora-2":
            if hd:
                raise ValueError("sora-2 不支持 hd，请使用 sora-2-pro")
            if duration == 25:
                raise ValueError("sora-2 不支持 25秒，请使用 sora-2-pro")

        if duration == 25 and hd:
            raise ValueError("duration=25 时 hd 不生效，请关闭 hd 或使用 10/15 秒")

        if notify_hook is not None:
            parsed = urlparse(notify_hook)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError("notify_hook 必须是合法的 URL")

        if images is not None and len(images) == 0:
            raise ValueError("images 不能为空列表")

        if not isinstance(hd, bool) or not isinstance(watermark, bool) or not isinstance(private, bool):
            raise ValueError("hd/watermark/private 必须是布尔值")

    async def create_video(
        self,
        prompt: str,
        image: Optional[str] = None,
        duration: int = 10,
        aspect_ratio: str = "16:9",
        **kwargs,
    ) -> str:
        if "duration" in kwargs:
            duration = int(kwargs.pop("duration"))
        if "aspect_ratio" in kwargs:
            aspect_ratio = str(kwargs.pop("aspect_ratio"))

        model = str(kwargs.pop("model", "sora-2"))
        images = kwargs.pop("images", None)
        hd = bool(kwargs.pop("hd", False))
        watermark = bool(kwargs.pop("watermark", False))
        private = bool(kwargs.pop("private", False))
        notify_hook = kwargs.pop("notify_hook", None)

        if images is None and image:
            images = [image]

        prepared_images = None
        if images is not None:
            if not isinstance(images, list):
                raise ValueError("images 必须是字符串数组")
            prepared_images = self._prepare_images([str(x) for x in images])

        self._validate_request(
            prompt=prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            duration=int(duration),
            hd=hd,
            watermark=watermark,
            private=private,
            notify_hook=notify_hook,
            images=prepared_images,
        )

        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
        }
        if prepared_images is not None:
            payload["images"] = prepared_images
        payload.update(
            {
                "aspect_ratio": aspect_ratio,
                "duration": int(duration),
                "hd": hd,
                "watermark": watermark,
                "private": private,
            }
        )
        if notify_hook:
            payload["notify_hook"] = notify_hook

        # RESTful: create a new generation task
        # POST {base_url}/v2/videos/generations
        endpoint = self._GENERATIONS_PATH

        response = await self._request("POST", endpoint, json=payload)
        task_id = response.get("task_id")
        if not task_id:
            raise ValueError("响应缺少 task_id")
        return str(task_id)

    async def query_task(self, task_id: str) -> Dict[str, Any]:
        # RESTful: query generation task status
        # GET {base_url}/v2/videos/generations/{task_id}
        # task_id must be URL-encoded to keep it path-safe.
        if not task_id or not str(task_id).strip():
            raise ValueError("task_id 不能为空")
        safe_task_id = quote(str(task_id), safe="")
        endpoint = f"{self._GENERATIONS_PATH}/{safe_task_id}"
        return await self._request("GET", endpoint)

    def parse_status(self, response: Dict[str, Any]) -> TaskStatus:
        status_map = {
            "pending": TaskStatus.PENDING,
            "processing": TaskStatus.PROCESSING,
            "completed": TaskStatus.COMPLETED,
            "failed": TaskStatus.FAILED,
            "cancelled": TaskStatus.CANCELLED,
        }
        return status_map.get(str(response.get("status", "")).lower(), TaskStatus.PENDING)
