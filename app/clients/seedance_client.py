from typing import Any, Dict, Optional

from app.core.base_client import BaseVideoClient
from app.models.schemas import TaskStatus


class SeedanceClient(BaseVideoClient):
    async def create_video(
        self,
        prompt: str,
        image: Optional[str] = None,
        first_frame: Optional[str] = None,
        last_frame: Optional[str] = None,
        **kwargs,
    ) -> str:
        if first_frame and last_frame:
            endpoint = "/v1/video/seedance/frames-to-video"
            payload: Dict[str, Any] = {
                "model": "seedance",
                "prompt": prompt,
                "first_frame": first_frame,
                "last_frame": last_frame,
                **kwargs,
            }
        elif image:
            endpoint = "/v1/video/seedance/image-to-video"
            payload = {
                "model": "seedance",
                "prompt": prompt,
                "image": image,
                **kwargs,
            }
        else:
            endpoint = "/v1/video/seedance/text-to-video"
            payload = {
                "model": "seedance",
                "prompt": prompt,
                **kwargs,
            }

        response = await self._request("POST", endpoint, json=payload)
        return str(response["task_id"])

    async def query_task(self, task_id: str) -> Dict[str, Any]:
        endpoint = f"/v1/video/seedance/tasks/{task_id}"
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

