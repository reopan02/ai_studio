from functools import lru_cache
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from app.api.deps import AuthContext, get_current_user
from app.config import get_settings
from app.core.task_manager import TaskManager
from app.models.schemas import TaskResponse, VideoGenerationRequest

router = APIRouter()


@lru_cache()
def get_task_manager() -> TaskManager:
    settings = get_settings()
    return TaskManager(api_key=settings.VIDEO_GEN_API_KEY)


@router.post("/video/generate", response_model=TaskResponse)
async def generate_video(
    request: VideoGenerationRequest,
    task_manager: TaskManager = Depends(get_task_manager),
    x_api_key: Optional[str] = Header(default=None),
    auth: AuthContext = Depends(get_current_user),
):
    try:
        task_id = await task_manager.create_task(request, api_key=x_api_key, owner_user_id=auth.user_id)
        task_status = await task_manager.get_task_status(task_id)
        return task_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/generate/sync", response_model=TaskResponse)
async def generate_video_sync(
    request: VideoGenerationRequest,
    task_manager: TaskManager = Depends(get_task_manager),
    x_api_key: Optional[str] = Header(default=None),
    auth: AuthContext = Depends(get_current_user),
):
    try:
        task_id = await task_manager.create_task(request, api_key=x_api_key, owner_user_id=auth.user_id)

        task = task_manager.tasks.get(task_id)
        if task:
            await task

        result = await task_manager.get_task_status(task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
