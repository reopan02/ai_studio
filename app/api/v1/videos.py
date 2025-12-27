from __future__ import annotations

import json
import logging

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.v1.video import get_task_manager
from app.core.encryption import EncryptionError, decrypt_for_user, encrypt_for_user
from app.core.task_manager import TaskManager
from app.db.session import get_db
from app.models.database import User, UserVideo
from app.models.schemas import (
    PaginatedResponse,
    UserVideoCreate,
    UserVideoDetail,
    UserVideoGenerateRequest,
    UserVideoSummary,
    UserVideoUpdate,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _json_dumps(data) -> bytes:
    return json.dumps(data, default=str, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _json_loads(payload: bytes):
    return json.loads(payload.decode("utf-8"))


def _ensure_owner(video: UserVideo, user: User) -> None:
    if user.is_admin:
        return
    if video.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")


@router.post("/videos/generate/sync", response_model=UserVideoSummary, status_code=status.HTTP_201_CREATED)
async def generate_and_store_video_sync(
    payload: UserVideoGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    task_manager: TaskManager = Depends(get_task_manager),
):
    try:
        task_id = await task_manager.create_task(payload.generation, api_key=None, owner_user_id=user.id)
        task = task_manager.tasks.get(task_id)
        if task:
            await task
        result = await task_manager.get_task_status(task_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Task result missing")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    request_dict = payload.generation.model_dump(mode="json")
    response_dict = result.model_dump(mode="json")

    try:
        request_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(request_dict))
        response_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(response_dict))
    except EncryptionError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    size_bytes = len(request_blob) + len(response_blob)
    if user.storage_used_bytes + size_bytes > user.storage_quota_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Storage quota exceeded")

    video = UserVideo(
        user_id=user.id,
        title=payload.title,
        model=str(payload.generation.model.value),
        prompt=payload.generation.prompt,
        status=str(result.status.value),
        video_url=result.video_url,
        request_encrypted=request_blob,
        response_encrypted=response_blob,
        size_bytes=size_bytes,
    )

    try:
        user.storage_used_bytes += size_bytes
        db.add(video)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to persist generated video for user_id=%s", user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save video record")

    await db.refresh(video)
    return video


@router.get("/videos", response_model=PaginatedResponse[UserVideoSummary])
async def list_videos(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    size: int = 50,
    search: Optional[str] = None,
    model: Optional[str] = None,
):
    page = max(1, int(page))
    size = max(1, min(200, int(size)))
    offset = (page - 1) * size

    # Base query for items
    stmt = select(UserVideo).options(
        load_only(
            UserVideo.id,
            UserVideo.user_id,
            UserVideo.title,
            UserVideo.model,
            UserVideo.prompt,
            UserVideo.status,
            UserVideo.video_url,
            UserVideo.size_bytes,
            UserVideo.created_at,
            UserVideo.updated_at,
        )
    )

    # Base query for count
    count_stmt = select(func.count()).select_from(UserVideo)

    # Apply filters
    filters = []
    if not user.is_admin:
        filters.append(UserVideo.user_id == user.id)
    if search:
        filters.append(UserVideo.title.ilike(f"%{search}%"))
    if model:
        filters.append(UserVideo.model == model)

    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)

    # Execute count
    total = (await db.execute(count_stmt)).scalar() or 0
    pages = (total + size - 1) // size

    # Execute items query
    stmt = stmt.order_by(desc(UserVideo.created_at)).offset(offset).limit(size)
    videos = (await db.execute(stmt)).scalars().all()

    return PaginatedResponse(
        items=videos,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/videos/{video_id}", response_model=UserVideoDetail)
async def get_video(
    video_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    video = await db.get(UserVideo, video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    _ensure_owner(video, user)

    try:
        request_payload = decrypt_for_user(user_id=video.user_id, blob=video.request_encrypted)
        response_payload = decrypt_for_user(user_id=video.user_id, blob=video.response_encrypted)
    except EncryptionError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return UserVideoDetail(
        **UserVideoSummary.model_validate(video).model_dump(),
        request=_json_loads(request_payload),
        response=_json_loads(response_payload),
    )


@router.patch("/videos/{video_id}", response_model=UserVideoSummary)
async def update_video(
    video_id: str,
    payload: UserVideoUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    video = await db.get(UserVideo, video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    _ensure_owner(video, user)

    if "title" in payload.model_fields_set:
        video.title = payload.title

    try:
        db.add(video)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to update video_id=%s for user_id=%s", video_id, user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update video record")
    await db.refresh(video)
    return video


@router.post("/videos", response_model=UserVideoSummary, status_code=status.HTTP_201_CREATED)
async def create_video_record(
    payload: UserVideoCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually save a generated video record to the repository.
    This is useful when the frontend manages the generation process directly.
    """
    video_url = str(payload.video_url or "").strip()
    if not video_url:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="video_url is required")

    existing = (
        await db.execute(
            select(UserVideo).where(
                UserVideo.user_id == user.id,
                UserVideo.video_url == video_url,
            )
        )
    ).scalars().first()
    if existing:
        return existing

    request_dict = {
        "model": payload.model,
        "prompt": payload.prompt,
        "metadata": payload.metadata
    }
    response_dict = {
        "video_url": payload.video_url,
        "status": payload.status
    }

    try:
        request_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(request_dict))
        response_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(response_dict))
    except EncryptionError as exc:
        logger.error(f"Encryption failed during record creation: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error during encryption preparation")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Encryption preparation failed")

    size_bytes = len(request_blob) + len(response_blob)
    if user.storage_used_bytes + size_bytes > user.storage_quota_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Storage quota exceeded")

    video = UserVideo(
        user_id=user.id,
        title=payload.title,
        model=payload.model,
        prompt=payload.prompt,
        status=payload.status,
        video_url=video_url,
        request_encrypted=request_blob,
        response_encrypted=response_blob,
        size_bytes=size_bytes,
    )

    try:
        user.storage_used_bytes += size_bytes
        db.add(video)
        db.add(user)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to persist video record for user_id=%s", user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save video record")

    await db.refresh(video)
    return video


@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    video = await db.get(UserVideo, video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    _ensure_owner(video, user)

    try:
        owner = await db.get(User, video.user_id)
        if owner:
            owner.storage_used_bytes = max(0, int(owner.storage_used_bytes) - int(video.size_bytes or 0))
            db.add(owner)
        await db.delete(video)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to delete video_id=%s for user_id=%s", video_id, user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete video record")
    return None
