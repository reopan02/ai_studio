from typing import Any, Dict, Optional

from app.core.base_client import BaseVideoClient
from app.models.schemas import TaskStatus


class NewModelClient(BaseVideoClient):
    async def create_video(
        self,
        prompt: str,
        image: Optional[str] = None,
        **kwargs,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": "newmodel",
            "prompt": prompt,
            **kwargs,
        }

        if image:
            endpoint = "/v1/video/newmodel/image-to-video"
            payload["image"] = image
        else:
            endpoint = "/v1/video/newmodel/text-to-video"

        response = await self._request("POST", endpoint, json=payload)
        return str(response["task_id"])

    async def query_task(self, task_id: str) -> Dict[str, Any]:
        endpoint = f"/v1/video/newmodel/tasks/{task_id}"
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

