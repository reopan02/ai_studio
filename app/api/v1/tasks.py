from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path

from app.api.deps import get_current_user
from app.api.v1.video import get_task_manager
from app.core.task_manager import TaskManager
from app.models.database import User
from app.models.schemas import TaskResponse

router = APIRouter()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str = Path(..., description="任务ID"),
    task_manager: TaskManager = Depends(get_task_manager),
    user: User = Depends(get_current_user),
):
    owner = task_manager.task_owners.get(task_id)
    if owner and (user.is_admin or owner == user.id):
        pass
    elif not owner and user.is_admin:
        pass
    else:
        raise HTTPException(status_code=404, detail="Task not found")

    task = await task_manager.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str = Path(..., description="任务ID"),
    task_manager: TaskManager = Depends(get_task_manager),
    user: User = Depends(get_current_user),
):
    owner = task_manager.task_owners.get(task_id)
    if owner and (user.is_admin or owner == user.id):
        pass
    elif not owner and user.is_admin:
        pass
    else:
        raise HTTPException(status_code=404, detail="Task not found or already completed")

    success = await task_manager.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or already completed")
    return {"message": "Task cancelled successfully"}


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(task_manager: TaskManager = Depends(get_task_manager), user: User = Depends(get_current_user)):
    if user.is_admin:
        return list(task_manager.results.values())

    allowed_task_ids = {tid for tid, owner in task_manager.task_owners.items() if owner == user.id}
    return [task for task_id, task in task_manager.results.items() if task_id in allowed_task_ids]
