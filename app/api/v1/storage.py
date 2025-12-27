from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.database import User
from app.models.schemas import StorageUsage

router = APIRouter()


@router.get("/storage/me", response_model=StorageUsage)
async def get_my_storage_usage(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _ = db  # keep signature consistent for future use
    return StorageUsage(quota_bytes=int(user.storage_quota_bytes), used_bytes=int(user.storage_used_bytes))

