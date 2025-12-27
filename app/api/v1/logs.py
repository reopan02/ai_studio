from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.database import ApiRequestLog, RequestCategory, User
from app.models.schemas import ApiRequestLogDetail, ApiRequestLogSummary, ApiRequestLogUpdate

router = APIRouter()


def _ensure_limit(limit: int) -> int:
    return max(1, min(200, limit))


@router.get("/logs", response_model=list[ApiRequestLogSummary])
async def list_logs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    method: Optional[str] = Query(default=None, max_length=10),
    path_contains: Optional[str] = Query(default=None, max_length=200),
    status_code: Optional[int] = Query(default=None, ge=100, le=599),
    category_id: Optional[str] = Query(default=None),
    started_after: Optional[datetime] = Query(default=None),
    started_before: Optional[datetime] = Query(default=None),
):
    stmt = select(ApiRequestLog)
    if not user.is_admin:
        stmt = stmt.where(ApiRequestLog.user_id == user.id)

    if method:
        stmt = stmt.where(ApiRequestLog.method == method.upper())
    if path_contains:
        stmt = stmt.where(ApiRequestLog.path.ilike(f"%{path_contains}%"))
    if status_code is not None:
        stmt = stmt.where(ApiRequestLog.response_status_code == status_code)
    if category_id is not None:
        stmt = stmt.where(ApiRequestLog.category_id == category_id)
    if started_after is not None:
        stmt = stmt.where(ApiRequestLog.started_at >= started_after)
    if started_before is not None:
        stmt = stmt.where(ApiRequestLog.started_at <= started_before)

    stmt = stmt.order_by(desc(ApiRequestLog.started_at)).offset(offset).limit(_ensure_limit(limit))
    logs = (await db.execute(stmt)).scalars().all()
    return logs


@router.get("/logs/{log_id}", response_model=ApiRequestLogDetail)
async def get_log(
    log_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = await db.get(ApiRequestLog, log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    if not user.is_admin and log.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return log


@router.patch("/logs/{log_id}", response_model=ApiRequestLogDetail)
async def update_log(
    log_id: str,
    payload: ApiRequestLogUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = await db.get(ApiRequestLog, log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    if not user.is_admin and log.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    if "category_id" in payload.model_fields_set:
        if payload.category_id is None:
            log.category_id = None
        else:
            category = await db.get(RequestCategory, payload.category_id)
            if not category:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
            if not user.is_admin and category.owner_user_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
            log.category_id = payload.category_id

    if "tags" in payload.model_fields_set:
        log.tags = payload.tags

    if "note" in payload.model_fields_set:
        log.note = payload.note

    try:
        db.add(log)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update log")
    await db.refresh(log)
    return log


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    log_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = await db.get(ApiRequestLog, log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    if not user.is_admin and log.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    try:
        await db.delete(log)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete log")
    return None
