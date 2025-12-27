from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.database import RequestCategory, User
from app.models.schemas import RequestCategoryCreate, RequestCategoryOut, RequestCategoryUpdate

router = APIRouter()


@router.post("/categories", response_model=RequestCategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: RequestCategoryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RequestCategory).where(
        RequestCategory.owner_user_id == user.id,
        RequestCategory.name == payload.name,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

    category = RequestCategory(
        owner_user_id=user.id,
        name=payload.name,
        description=payload.description,
    )

    try:
        db.add(category)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create category")
    await db.refresh(category)
    return category


@router.get("/categories", response_model=list[RequestCategoryOut])
async def list_categories(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(RequestCategory)
        .where(RequestCategory.owner_user_id == user.id)
        .order_by(RequestCategory.created_at.desc())
    )
    categories = (await db.execute(stmt)).scalars().all()
    return categories


@router.patch("/categories/{category_id}", response_model=RequestCategoryOut)
async def update_category(
    category_id: str,
    payload: RequestCategoryUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    category = await db.get(RequestCategory, category_id)
    if not category or category.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if "name" in payload.model_fields_set and payload.name is not None:
        stmt = select(RequestCategory).where(
            RequestCategory.owner_user_id == user.id,
            RequestCategory.name == payload.name,
            RequestCategory.id != category_id,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists")
        category.name = payload.name

    if "description" in payload.model_fields_set:
        category.description = payload.description

    try:
        db.add(category)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update category")
    await db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    category = await db.get(RequestCategory, category_id)
    if not category or category.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    try:
        await db.delete(category)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete category")
    return None
