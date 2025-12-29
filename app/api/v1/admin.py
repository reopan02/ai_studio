from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.api.deps import require_admin
from app.core.datetime_utils import utc_now
from app.db.session import get_db
from app.models.database import User, UserImage, UserLoginLog, UserSession, UserVideo
from app.models.schemas import (
    AdminLoginAttempt,
    AdminSystemStats,
    AdminUserDetail,
    AdminUserSummary,
    AdminUserUpdate,
    UserPublic,
    UserQuotaUpdate,
)

router = APIRouter()


@router.patch("/admin/users/{user_id}/quota", response_model=UserPublic)
async def update_user_quota(
    user_id: str,
    payload: UserQuotaUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.storage_quota_bytes = int(payload.storage_quota_bytes)
    user.storage_used_bytes = max(0, int(user.storage_used_bytes))

    try:
        db.add(user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")
    await db.refresh(user)
    return user


@router.get("/admin/users", response_model=list[AdminUserSummary])
async def list_users(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    is_active: bool | None = None,
    is_admin: bool | None = None,
):
    limit = max(1, min(200, int(limit)))
    offset = max(0, int(offset))

    stmt = select(User).options(
        load_only(
            User.id,
            User.username,
            User.email,
            User.is_active,
            User.is_admin,
            User.storage_quota_bytes,
            User.storage_used_bytes,
            User.created_at,
            User.last_login_at,
        )
    )

    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.where(or_(User.username.ilike(needle), User.email.ilike(needle)))
    if is_active is not None:
        stmt = stmt.where(User.is_active.is_(bool(is_active)))
    if is_admin is not None:
        stmt = stmt.where(User.is_admin.is_(bool(is_admin)))

    stmt = stmt.order_by(desc(User.created_at)).offset(offset).limit(limit)
    users = (await db.execute(stmt)).scalars().all()
    return users


@router.get("/admin/users/{user_id}", response_model=AdminUserDetail)
async def get_user_detail(
    user_id: str,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    total_videos = (
        await db.execute(select(func.count(UserVideo.id)).where(UserVideo.user_id == user.id))
    ).scalar_one()
    total_images = (
        await db.execute(select(func.count(UserImage.id)).where(UserImage.user_id == user.id))
    ).scalar_one()

    now = utc_now()
    active_sessions = (
        await db.execute(
            select(func.count(UserSession.id)).where(
                UserSession.user_id == user.id,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > now,
            )
        )
    ).scalar_one()

    logs = (
        await db.execute(
            select(UserLoginLog)
            .options(
                load_only(
                    UserLoginLog.id,
                    UserLoginLog.user_id,
                    UserLoginLog.username_or_email,
                    UserLoginLog.success,
                    UserLoginLog.failure_reason,
                    UserLoginLog.ip_address,
                    UserLoginLog.user_agent,
                    UserLoginLog.created_at,
                )
            )
            .where(UserLoginLog.user_id == user.id)
            .order_by(desc(UserLoginLog.created_at))
            .limit(10)
        )
    ).scalars().all()

    recent_attempts = [AdminLoginAttempt.model_validate(item) for item in logs]

    return AdminUserDetail(
        **AdminUserSummary.model_validate(user).model_dump(),
        total_video_count=int(total_videos or 0),
        total_image_count=int(total_images or 0),
        active_session_count=int(active_sessions or 0),
        recent_login_attempts=recent_attempts,
    )


@router.patch("/admin/users/{user_id}", response_model=AdminUserSummary)
async def update_user(
    user_id: str,
    payload: AdminUserUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if "email" in payload.model_fields_set:
        new_email = str(payload.email).strip() if payload.email else ""
        if not new_email:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="email is required")
        if new_email != user.email:
            existing = (
                await db.execute(
                    select(User.id).where(
                        User.email == new_email,
                        User.id != user.id,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Email already exists",
                )
            user.email = new_email

    if "is_active" in payload.model_fields_set:
        user.is_active = bool(payload.is_active)

    if "is_admin" in payload.model_fields_set:
        user.is_admin = bool(payload.is_admin)

    if "storage_quota_bytes" in payload.model_fields_set:
        user.storage_quota_bytes = int(payload.storage_quota_bytes or 0)
        user.storage_used_bytes = max(0, int(user.storage_used_bytes or 0))

    try:
        db.add(user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")
    await db.refresh(user)
    return user


@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if user_id == admin_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        await db.execute(delete(UserSession).where(UserSession.user_id == user_id))
        await db.execute(delete(UserVideo).where(UserVideo.user_id == user_id))
        await db.execute(delete(UserImage).where(UserImage.user_id == user_id))
        await db.delete(user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user")
    return None


@router.get("/admin/stats", response_model=AdminSystemStats)
async def get_system_stats(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    total_user_count = (await db.execute(select(func.count(User.id)))).scalar_one()
    active_user_count = (
        await db.execute(select(func.count(User.id)).where(User.is_active.is_(True)))
    ).scalar_one()

    total_storage_used_bytes = (
        await db.execute(select(func.coalesce(func.sum(User.storage_used_bytes), 0)))
    ).scalar_one()
    total_storage_quota_bytes = (
        await db.execute(select(func.coalesce(func.sum(User.storage_quota_bytes), 0)))
    ).scalar_one()

    total_video_count = (await db.execute(select(func.count(UserVideo.id)))).scalar_one()
    total_image_count = (await db.execute(select(func.count(UserImage.id)))).scalar_one()

    now = utc_now()
    active_session_count = (
        await db.execute(
            select(func.count(UserSession.id)).where(
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > now,
            )
        )
    ).scalar_one()

    return AdminSystemStats(
        total_user_count=int(total_user_count or 0),
        active_user_count=int(active_user_count or 0),
        total_storage_used_bytes=int(total_storage_used_bytes or 0),
        total_storage_quota_bytes=int(total_storage_quota_bytes or 0),
        total_video_count=int(total_video_count or 0),
        total_image_count=int(total_image_count or 0),
        active_session_count=int(active_session_count or 0),
    )
