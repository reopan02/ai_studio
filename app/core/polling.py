from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Dict, Optional

from app.config import get_settings
from app.core.base_client import BaseVideoClient
from app.models.schemas import ProgressCallback, TaskStatus


class TaskPoller:
    def __init__(
        self,
        client: BaseVideoClient,
        task_id: str,
        callback: Optional[Callable[[ProgressCallback], Awaitable[None] | None]] = None,
    ):
        self.client = client
        self.task_id = task_id
        self.callback = callback
        self.attempts = 0
        self.error_retries = 0

    async def poll_until_complete(self) -> Dict[str, Any]:
        settings = get_settings()

        while self.attempts < settings.POLLING_MAX_ATTEMPTS:
            try:
                response = await self.client.query_task(self.task_id)
                status = self.client.parse_status(response)
                progress = int(response.get("progress", 0) or 0)

                if self.callback:
                    callback_data = ProgressCallback(
                        task_id=self.task_id,
                        progress=progress,
                        status=status,
                        message=str(response.get("message", "") or ""),
                    )
                    await self._safe_callback(callback_data)

                if status == TaskStatus.COMPLETED:
                    return response
                if status == TaskStatus.FAILED:
                    raise RuntimeError(str(response.get("error") or "Task failed"))
                if status == TaskStatus.CANCELLED:
                    raise RuntimeError("Task was cancelled")

                self.attempts += 1
                await asyncio.sleep(settings.POLLING_INTERVAL)
            except Exception:
                self.error_retries += 1
                if self.error_retries > settings.MAX_RETRIES:
                    raise
                await asyncio.sleep(settings.POLLING_INTERVAL)

        raise TimeoutError(
            f"Task {self.task_id} polling timeout after {settings.POLLING_MAX_ATTEMPTS} attempts"
        )

    async def _safe_callback(self, data: ProgressCallback) -> None:
        try:
            if asyncio.iscoroutinefunction(self.callback):
                await self.callback(data)
            else:
                self.callback(data)
        except Exception:
            return

