from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.database import TargetType, User, UserTargetDescription
from app.models.schemas import (
    TargetTypeCreate,
    TargetTypeUpdate,
    TargetTypeOut,
    TargetTypeListResponse,
    UserTargetDescriptionCreate,
    UserTargetDescriptionUpdate,
    UserTargetDescriptionOut,
    UserTargetDescriptionListResponse,
)

router = APIRouter()

# Default target types to initialize
DEFAULT_TARGET_TYPES = [
    {
        "id": "target-main",
        "name": "主图",
        "placeholder": "请描述主图的展示重点，如产品摆放方式、突出的卖点...",
        "default_template": "适合电商主图展示的产品图，突出产品整体外观，简洁大方",
        "sort_order": 0,
    },
    {
        "id": "target-detail",
        "name": "详情页",
        "placeholder": "请描述详情页需要展示的产品细节或使用场景...",
        "default_template": "适合详情页的产品展示图，展现产品细节和使用场景",
        "sort_order": 1,
    },
    {
        "id": "target-poster",
        "name": "海报",
        "placeholder": "请描述海报的主题和风格，如促销活动、节日氛围...",
        "default_template": "具有视觉冲击力的营销海报风格，适合活动推广",
        "sort_order": 2,
    },
    {
        "id": "target-white",
        "name": "白底图",
        "placeholder": "请描述白底图的拍摄角度和展示方式...",
        "default_template": "纯白色背景的产品图，适合平台商品展示",
        "sort_order": 3,
    },
    {
        "id": "target-scene",
        "name": "场景图",
        "placeholder": "请描述期望的使用场景和环境氛围...",
        "default_template": "产品在真实使用场景中的展示图，增强代入感",
        "sort_order": 4,
    },
]


async def ensure_default_target_types(db: AsyncSession) -> None:
    """Ensure default target types exist in database."""
    result = await db.execute(select(TargetType).limit(1))
    if result.scalar_one_or_none() is not None:
        return  # Already has data

    for tt_data in DEFAULT_TARGET_TYPES:
        tt = TargetType(**tt_data)
        db.add(tt)
    await db.commit()


@router.get("/target-types", response_model=TargetTypeListResponse)
async def list_target_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all target types ordered by sort_order.

    Returns a list of target types that can be used for ecommerce image generation.
    Each type includes a name, placeholder text, and default prompt template.
    """
    # Ensure default types exist
    await ensure_default_target_types(db)

    result = await db.execute(
        select(TargetType).order_by(TargetType.sort_order, TargetType.created_at)
    )
    target_types = result.scalars().all()

    return TargetTypeListResponse(
        target_types=[TargetTypeOut.model_validate(tt) for tt in target_types]
    )


@router.post("/target-types", response_model=TargetTypeOut, status_code=status.HTTP_201_CREATED)
async def create_target_type(
    data: TargetTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new target type. Admin only.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Check for duplicate name
    result = await db.execute(
        select(TargetType).where(TargetType.name == data.name)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Target type with name '{data.name}' already exists"
        )

    target_type = TargetType(
        id=str(uuid4()),
        name=data.name,
        placeholder=data.placeholder,
        default_template=data.default_template,
        sort_order=data.sort_order or 0,
    )
    db.add(target_type)
    await db.commit()
    await db.refresh(target_type)

    return TargetTypeOut.model_validate(target_type)


@router.get("/target-types/{target_type_id}", response_model=TargetTypeOut)
async def get_target_type(
    target_type_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific target type by ID.
    """
    result = await db.execute(
        select(TargetType).where(TargetType.id == target_type_id)
    )
    target_type = result.scalar_one_or_none()

    if target_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target type not found"
        )

    return TargetTypeOut.model_validate(target_type)


@router.put("/target-types/{target_type_id}", response_model=TargetTypeOut)
async def update_target_type(
    target_type_id: str,
    data: TargetTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a target type. Admin only.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    result = await db.execute(
        select(TargetType).where(TargetType.id == target_type_id)
    )
    target_type = result.scalar_one_or_none()

    if target_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target type not found"
        )

    # Check for duplicate name if name is being changed
    if data.name is not None and data.name != target_type.name:
        name_check = await db.execute(
            select(TargetType).where(TargetType.name == data.name)
        )
        if name_check.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Target type with name '{data.name}' already exists"
            )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(target_type, key, value)

    await db.commit()
    await db.refresh(target_type)

    return TargetTypeOut.model_validate(target_type)


@router.delete("/target-types/{target_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target_type(
    target_type_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a target type. Admin only.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    result = await db.execute(
        select(TargetType).where(TargetType.id == target_type_id)
    )
    target_type = result.scalar_one_or_none()

    if target_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target type not found"
        )

    await db.execute(
        delete(TargetType).where(TargetType.id == target_type_id)
    )
    await db.commit()

    return None


# ============================================
# User Target Description Endpoints
# ============================================

@router.get("/target-descriptions", response_model=UserTargetDescriptionListResponse)
async def list_user_target_descriptions(
    target_type_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all saved target descriptions for the current user.
    Optionally filter by target_type_id.
    """
    query = select(UserTargetDescription).where(
        UserTargetDescription.user_id == current_user.id
    )

    if target_type_id:
        query = query.where(UserTargetDescription.target_type_id == target_type_id)

    query = query.order_by(UserTargetDescription.created_at.desc())

    result = await db.execute(query)
    descriptions = result.scalars().all()

    return UserTargetDescriptionListResponse(
        descriptions=[UserTargetDescriptionOut.model_validate(d) for d in descriptions]
    )


@router.post("/target-descriptions", response_model=UserTargetDescriptionOut, status_code=status.HTTP_201_CREATED)
async def create_user_target_description(
    data: UserTargetDescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new saved target description.
    """
    # Verify target type exists
    result = await db.execute(
        select(TargetType).where(TargetType.id == data.target_type_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target type not found"
        )

    description = UserTargetDescription(
        id=str(uuid4()),
        user_id=current_user.id,
        target_type_id=data.target_type_id,
        name=data.name.strip(),
        description=data.description.strip(),
    )
    db.add(description)
    await db.commit()
    await db.refresh(description)

    return UserTargetDescriptionOut.model_validate(description)


@router.get("/target-descriptions/{description_id}", response_model=UserTargetDescriptionOut)
async def get_user_target_description(
    description_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific saved target description.
    """
    result = await db.execute(
        select(UserTargetDescription).where(
            UserTargetDescription.id == description_id,
            UserTargetDescription.user_id == current_user.id,
        )
    )
    description = result.scalar_one_or_none()

    if description is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved description not found"
        )

    return UserTargetDescriptionOut.model_validate(description)


@router.put("/target-descriptions/{description_id}", response_model=UserTargetDescriptionOut)
async def update_user_target_description(
    description_id: str,
    data: UserTargetDescriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a saved target description.
    """
    result = await db.execute(
        select(UserTargetDescription).where(
            UserTargetDescription.id == description_id,
            UserTargetDescription.user_id == current_user.id,
        )
    )
    description = result.scalar_one_or_none()

    if description is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved description not found"
        )

    if data.name is not None:
        description.name = data.name.strip()
    if data.description is not None:
        description.description = data.description.strip()

    await db.commit()
    await db.refresh(description)

    return UserTargetDescriptionOut.model_validate(description)


@router.delete("/target-descriptions/{description_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_target_description(
    description_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a saved target description.
    """
    result = await db.execute(
        select(UserTargetDescription).where(
            UserTargetDescription.id == description_id,
            UserTargetDescription.user_id == current_user.id,
        )
    )
    description = result.scalar_one_or_none()

    if description is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved description not found"
        )

    await db.execute(
        delete(UserTargetDescription).where(UserTargetDescription.id == description_id)
    )
    await db.commit()

    return None
