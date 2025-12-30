from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.database import Product, User
from app.models.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductSummary,
    ProductDetail,
    ProductListResponse,
)
from app.core.product_storage import (
    save_product_image,
    delete_product_image,
    compress_image_if_needed,
    get_image_format,
    image_to_base64,
    base64_to_image,
    ProductStorageError,
)
from app.clients.llm_client import (
    recognize_product,
    create_manual_recognition_result,
    ProductRecognitionError,
)

router = APIRouter()


@router.post("/products", response_model=ProductDetail, status_code=status.HTTP_201_CREATED)
async def create_product(
    image: UploadFile = File(...),
    name: Optional[str] = Form(None),
    dimensions: Optional[str] = Form(None),
    features: Optional[str] = Form(None),  # JSON string
    characteristics: Optional[str] = Form(None),  # JSON string
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new product with image upload and AI recognition.

    - Upload a product image
    - AI will automatically extract product attributes
    - Manual attributes can override AI results
    - Enforces storage quota
    """
    import json

    # Read image data
    image_data = await image.read()

    # Check image size
    if len(image_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image file"
        )

    # Check storage quota
    if current_user.storage_used_bytes + len(image_data) > current_user.storage_quota_bytes:
        available = current_user.storage_quota_bytes - current_user.storage_used_bytes
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Storage quota exceeded",
                "quota_bytes": current_user.storage_quota_bytes,
                "used_bytes": current_user.storage_used_bytes,
                "available_bytes": available,
                "requested_bytes": len(image_data),
            }
        )

    # Detect image format
    try:
        img_format = get_image_format(image_data)
    except ProductStorageError:
        img_format = "jpg"

    # Compress image if needed for AI recognition
    compressed_data, was_compressed = compress_image_if_needed(image_data)

    # Generate product ID
    product_id = str(uuid4())

    # AI recognition (with fallback to manual entry)
    recognition_result = None
    recognition_metadata = None
    ai_confidence = 0.0

    try:
        # Convert to base64 for AI recognition
        image_base64 = image_to_base64(compressed_data)

        # Call AI recognition
        recognition_result = await recognize_product(image_base64)

        ai_confidence = recognition_result.confidence
        recognition_metadata = {
            "recognized_at": datetime.utcnow().isoformat(),
            "model": "structllm",
            "confidence": recognition_result.confidence,
            "original_result": {
                "name": recognition_result.name,
                "dimensions": recognition_result.dimensions,
                "features": recognition_result.features,
                "characteristics": recognition_result.characteristics,
            },
            "was_compressed": was_compressed,
        }

    except (ProductRecognitionError, Exception) as e:
        # AI recognition failed - use manual entry or defaults
        recognition_result = create_manual_recognition_result(
            name=name or "未命名产品",
            dimensions=dimensions,
            features=json.loads(features) if features else [],
            characteristics=json.loads(characteristics) if characteristics else [],
        )
        recognition_metadata = {
            "error": str(e),
            "fallback": "manual_entry"
        }

    # Override AI results with manual input if provided
    final_name = name if name else recognition_result.name
    final_dimensions = dimensions if dimensions else recognition_result.dimensions
    final_features = json.loads(features) if features else recognition_result.features
    final_characteristics = json.loads(characteristics) if characteristics else recognition_result.characteristics

    # Save image to file system
    try:
        image_url, image_size = save_product_image(
            user_id=current_user.id,
            product_id=product_id,
            image_data=image_data,
            original_format=img_format
        )
    except ProductStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save product image: {str(e)}"
        )

    # Create product record
    product = Product(
        id=product_id,
        user_id=current_user.id,
        name=final_name,
        dimensions=final_dimensions,
        features=final_features,
        characteristics=final_characteristics,
        original_image_url=image_url,
        recognition_confidence=ai_confidence,
        recognition_metadata=recognition_metadata,
        image_size_bytes=image_size,
    )

    db.add(product)

    # Update user storage quota
    stmt = (
        update(User)
        .where(User.id == current_user.id)
        .values(storage_used_bytes=User.storage_used_bytes + image_size)
    )
    await db.execute(stmt)

    await db.commit()
    await db.refresh(product)

    return product


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    offset: int = 0,
    limit: int = 20,
    name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List user's products with pagination and filtering.

    - offset: Number of products to skip
    - limit: Maximum number of products to return (max 100)
    - name: Filter by product name (case-insensitive partial match)
    """
    # Limit bounds
    limit = min(limit, 100)

    # Build query
    query = select(Product).where(Product.user_id == current_user.id)

    # Apply name filter if provided
    if name:
        query = query.where(Product.name.ilike(f"%{name}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(Product.created_at.desc()).offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        products=[ProductSummary.model_validate(p) for p in products],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/products/{product_id}", response_model=ProductDetail)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get product details by ID.

    Returns full product information including recognition metadata.
    """
    # Query product
    stmt = select(Product).where(
        Product.id == product_id,
        Product.user_id == current_user.id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        # Return 404 for non-existent or other user's products (security)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.put("/products/{product_id}", response_model=ProductDetail)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update product attributes.

    Allows manual correction of AI-recognized attributes.
    """
    # Query product
    stmt = select(Product).where(
        Product.id == product_id,
        Product.user_id == current_user.id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Update fields if provided
    update_data = product_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_endpoint(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a product and reclaim storage quota.

    - Deletes product record from database
    - Removes image file from file system
    - Reclaims storage quota
    """
    # Query product
    stmt = select(Product).where(
        Product.id == product_id,
        Product.user_id == current_user.id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Delete image file
    try:
        delete_product_image(product.original_image_url)
    except ProductStorageError:
        # Log error but continue with database deletion
        pass

    # Reclaim storage quota
    stmt = (
        update(User)
        .where(User.id == current_user.id)
        .values(storage_used_bytes=User.storage_used_bytes - product.image_size_bytes)
    )
    await db.execute(stmt)

    # Delete product record
    await db.delete(product)
    await db.commit()

    return None
