from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.database import User
from app.models.schemas import UserPublic, UserQuotaUpdate

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
