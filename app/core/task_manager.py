from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Callable, Dict, Optional
from uuid import uuid4

from app.clients.new_model_client import NewModelClient
from app.clients.seedance_client import SeedanceClient
from app.clients.sora_client import Sora2Client
from app.clients.veo_client import VeoClient
from app.config import get_settings
from app.core.base_client import BaseVideoClient
from app.core.polling import TaskPoller
from app.models.schemas import ModelType, ProgressCallback, TaskResponse, TaskStatus, VideoGenerationRequest


class TaskManager:
    def __init__(self, api_key: str):
        settings = get_settings()
        self.api_key = api_key
        self.tasks: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, TaskResponse] = {}
        self.task_owners: Dict[str, str] = {}
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_TASKS)

    def _get_client(self, model: ModelType, api_key: Optional[str] = None) -> BaseVideoClient:
        client_map = {
            ModelType.SORA2: Sora2Client,
            ModelType.VEO: VeoClient,
            ModelType.SEEDANCE: SeedanceClient,
            ModelType.NEWMODEL: NewModelClient,
        }
        client_class = client_map.get(model)
        if not client_class:
            raise ValueError(f"Unsupported model: {model}")
        return client_class(api_key or self.api_key)

    async def create_task(
        self,
        request: VideoGenerationRequest,
        callback: Optional[Callable[[ProgressCallback], None]] = None,
        api_key: Optional[str] = None,
        owner_user_id: Optional[str] = None,
    ) -> str:
        task_id = str(uuid4())
        if owner_user_id:
            self.task_owners[task_id] = str(owner_user_id)

        now = datetime.now()
        self.results[task_id] = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            progress=0,
            created_at=now,
            updated_at=now,
        )

        async_task = asyncio.create_task(self._execute_task(task_id, request, callback, api_key))
        self.tasks[task_id] = async_task

        return task_id

    async def _execute_task(
        self,
        task_id: str,
        request: VideoGenerationRequest,
        callback: Optional[Callable[[ProgressCallback], None]],
        api_key: Optional[str] = None,
    ) -> None:
        async with self.semaphore:
            client: Optional[BaseVideoClient] = None
            try:
                self._update_task_status(task_id, TaskStatus.PROCESSING, progress=0)

                client = self._get_client(request.model, api_key)

                extra_params = dict(request.extra_params or {})
                if request.model == ModelType.SORA2:
                    remote_task_id = await client.create_video(
                        prompt=request.prompt,
                        image=request.image,
                        duration=request.duration,
                        aspect_ratio=request.aspect_ratio,
                        **extra_params,
                    )
                else:
                    remote_task_id = await client.create_video(
                        prompt=request.prompt,
                        image=request.image,
                        duration=request.duration,
                        aspect_ratio=request.aspect_ratio,
                        resolution=request.resolution,
                        **extra_params,
                    )

                poller = TaskPoller(client, remote_task_id, callback)
                result = await poller.poll_until_complete()

                self._update_task_status(
                    task_id,
                    TaskStatus.COMPLETED,
                    progress=100,
                    video_url=result.get("video_url"),
                    video_base64=result.get("video_base64"),
                )
            except Exception as e:
                self._update_task_status(task_id, TaskStatus.FAILED, error=str(e))
                raise
            finally:
                if client:
                    await client.close()

    def _update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        progress: Optional[int] = None,
        video_url: Optional[str] = None,
        video_base64: Optional[str] = None,
        error: Optional[str] = None,
        message: Optional[str] = None,
    ) -> None:
        task = self.results.get(task_id)
        if not task:
            return

        task.status = status
        if progress is not None:
            task.progress = progress
        if video_url is not None:
            task.video_url = video_url
        if video_base64 is not None:
            task.video_base64 = video_base64
        if error is not None:
            task.error = error
        if message is not None:
            task.message = message
        task.updated_at = datetime.now()

    async def get_task_status(self, task_id: str) -> Optional[TaskResponse]:
        return self.results.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and not task.done():
            task.cancel()
            self._update_task_status(task_id, TaskStatus.CANCELLED)
            return True
        return False

    async def wait_all(self) -> None:
        if self.tasks:
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)
