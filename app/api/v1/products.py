from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.database import Product, ProductImage, User
from app.models.schemas import (
    ProductUpdate,
    ProductSummary,
    ProductImageSummary,
    ProductDetail,
    ProductListResponse,
    ProductRecognitionResponse,
)
from app.core.product_storage import (
    save_product_image,
    delete_product_image,
    get_image_format,
    prepare_image_for_llm,
    image_to_base64,
    ProductStorageError,
)
from app.clients.llm_client import (
    recognize_product_with_metadata,
    create_manual_recognition_result,
    ProductRecognitionError,
)

router = APIRouter()


def build_product_detail_response(product: Product, images: List[ProductImage]) -> ProductDetail:
    if images:
        image_payload = [ProductImageSummary.model_validate(img) for img in images]
    else:
        image_payload = [
            ProductImageSummary(
                id=product.id,
                image_url=product.original_image_url,
                image_size_bytes=product.image_size_bytes,
                is_primary=True,
                created_at=product.created_at,
                updated_at=product.updated_at,
            )
        ]

    product_data = ProductDetail.model_validate(product).model_dump()
    product_data["images"] = image_payload
    product_data["image_count"] = len(image_payload)
    return ProductDetail(**product_data)


@router.post("/products/recognize", response_model=ProductRecognitionResponse)
async def recognize_product_preview(
    image: UploadFile = File(...),
    raw_text: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
):
    """
    Preview recognition: extract product attributes from image + optional raw text.

    This endpoint performs AI recognition but does NOT create a product record.
    Use this to prefill a form before the user saves.

    - Upload a product image (required)
    - Optionally provide unstructured text for additional context
    - Returns structured fields without persisting anything
    """
    # Read image data
    image_data = await image.read()

    # Check image size
    if len(image_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image file"
        )

    # Detect image format
    try:
        detected_format = get_image_format(image_data)
    except ProductStorageError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid or unsupported image file",
        )

    if detected_format not in {"jpeg", "png"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only JPEG and PNG images are supported",
        )

    # Prepare image for AI recognition (convert/compress for LLM input)
    llm_image_data, preprocessing = prepare_image_for_llm(image_data)
    llm_mime_type = "image/jpeg" if preprocessing["processed_format"] in {"jpg", "jpeg"} else "image/png"

    # AI recognition with optional raw text
    try:
        # Convert to base64 for AI recognition
        image_base64 = image_to_base64(llm_image_data)

        # Call AI recognition with raw_text
        recognition_result, llm_metadata = await recognize_product_with_metadata(
            image_base64,
            mime_type=llm_mime_type,
            raw_text=raw_text
        )

        recognition_metadata = {
            "recognized_at": datetime.utcnow().isoformat(),
            "model": "structllm",
            "confidence": recognition_result.confidence,
            "preprocessing": preprocessing,
            "llm": llm_metadata,
        }

        return ProductRecognitionResponse(
            name=recognition_result.name,
            dimensions=recognition_result.dimensions,
            features=recognition_result.features,
            characteristics=recognition_result.characteristics,
            confidence=recognition_result.confidence,
            metadata=recognition_metadata,
        )

    except (ProductRecognitionError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product recognition failed: {str(e)}"
        )


@router.post("/products", response_model=ProductDetail, status_code=status.HTTP_201_CREATED)
async def create_product(
    images: Optional[List[UploadFile]] = File(None),
    image: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None),
    dimensions: Optional[str] = Form(None),
    features: Optional[str] = Form(None),  # JSON string
    characteristics: Optional[str] = Form(None),  # JSON string
    recognition_mode: Optional[str] = Form("auto"),  # auto | manual | prefill
    recognition_confidence: Optional[float] = Form(None),  # For prefill mode
    recognition_metadata_json: Optional[str] = Form(None),  # For prefill mode (JSON string)
    primary_index: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new product with image uploads.

    Recognition modes:
    - auto (default): Run AI recognition to extract product attributes
    - manual: Skip AI and use only manually entered fields
    - prefill: Skip AI but preserve preview recognition confidence/metadata

    - Upload one or more product images (required)
    - The primary image (default: first) is used for AI recognition and list thumbnails
    - Manual attributes override AI results in 'auto' mode
    - Enforces storage quota
    """
    import json
    from pathlib import Path

    if name is not None and len(name) > 200:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="name must be <= 200 characters")
    if dimensions is not None and len(dimensions) > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="dimensions must be <= 100 characters"
        )

    def parse_string_list(value: Optional[str], field_name: str) -> Optional[List[str]]:
        if value is None:
            return None
        try:
            parsed: Any = json.loads(value)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} must be a JSON array of strings",
            )
        if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} must be a JSON array of strings",
            )
        return parsed

    manual_features = parse_string_list(features, "features")
    manual_characteristics = parse_string_list(characteristics, "characteristics")

    uploads: List[UploadFile] = []
    if images:
        uploads.extend(images)
    if image and image not in uploads:
        uploads.append(image)

    if not uploads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one image file is required",
        )

    image_payloads: List[Dict[str, Any]] = []
    for idx, upload in enumerate(uploads):
        image_data = await upload.read()
        if len(image_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Empty image file at index {idx}",
            )

        try:
            detected_format = get_image_format(image_data)
        except ProductStorageError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid or unsupported image file",
            )

        if detected_format not in {"jpeg", "png"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only JPEG and PNG images are supported",
            )

        filename_ext = Path(upload.filename or "").suffix.lower().lstrip(".")
        if detected_format == "png":
            img_format = "png"
        else:
            img_format = filename_ext if filename_ext in {"jpg", "jpeg"} else "jpeg"

        image_payloads.append(
            {
                "data": image_data,
                "format": img_format,
                "filename": upload.filename or f"image-{idx}",
            }
        )

    if primary_index is None:
        primary_index = 0
    if primary_index < 0 or primary_index >= len(image_payloads):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="primary_index is out of range",
        )

    primary_payload = image_payloads[primary_index]

    # Validate recognition_mode
    if recognition_mode not in {"auto", "manual", "prefill"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="recognition_mode must be 'auto', 'manual', or 'prefill'"
        )

    # Prepare image for AI recognition (convert/compress for LLM input only)
    llm_image_data, preprocessing = prepare_image_for_llm(primary_payload["data"])
    llm_mime_type = "image/jpeg" if preprocessing["processed_format"] in {"jpg", "jpeg"} else "image/png"

    # AI recognition based on mode
    recognition_result = None
    recognition_metadata = None
    ai_confidence = 0.0

    if recognition_mode == "auto":
        # Run AI recognition
        try:
            # Convert to base64 for AI recognition
            image_base64 = image_to_base64(llm_image_data)

            # Call AI recognition
            recognition_result, llm_metadata = await recognize_product_with_metadata(image_base64, mime_type=llm_mime_type)

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
                "preprocessing": preprocessing,
                "llm": llm_metadata,
            }

        except (ProductRecognitionError, Exception) as e:
            # AI recognition failed - use manual entry or defaults
            recognition_result = create_manual_recognition_result(
                name=name or "未命名产品",
                dimensions=dimensions,
                features=manual_features or [],
                characteristics=manual_characteristics or [],
            )
            recognition_metadata = {
                "error": str(e),
                "fallback": "manual_entry",
                "preprocessing": preprocessing,
            }

    elif recognition_mode == "manual":
        # Manual mode: skip AI entirely, use confidence=0.0
        recognition_result = create_manual_recognition_result(
            name=name or "未命名产品",
            dimensions=dimensions,
            features=manual_features or [],
            characteristics=manual_characteristics or [],
        )
        recognition_metadata = {
            "mode": "manual",
            "preprocessing": preprocessing,
        }

    elif recognition_mode == "prefill":
        # Prefill mode: use preview recognition confidence/metadata
        ai_confidence = recognition_confidence if recognition_confidence is not None else 0.0

        # Validate confidence range
        if ai_confidence < 0.0:
            ai_confidence = 0.0
        elif ai_confidence > 1.0:
            ai_confidence = 1.0

        # Parse recognition_metadata_json if provided
        if recognition_metadata_json:
            try:
                recognition_metadata = json.loads(recognition_metadata_json)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="recognition_metadata_json must be valid JSON"
                )
        else:
            recognition_metadata = {
                "mode": "prefill",
                "preprocessing": preprocessing,
            }

        # Create recognition result from manual fields
        recognition_result = create_manual_recognition_result(
            name=name or "未命名产品",
            dimensions=dimensions,
            features=manual_features or [],
            characteristics=manual_characteristics or [],
        )
        # Override confidence since this is from prefill
        recognition_result.confidence = ai_confidence

    if recognition_metadata is None:
        recognition_metadata = {}
    if isinstance(recognition_metadata, dict):
        recognition_metadata["image_count"] = len(image_payloads)
        recognition_metadata["primary_index"] = primary_index
    else:
        recognition_metadata = {
            "image_count": len(image_payloads),
            "primary_index": primary_index,
            "metadata": recognition_metadata,
        }

    # Override AI results with manual input if provided
    final_name = name if name else recognition_result.name
    final_dimensions = dimensions if dimensions else recognition_result.dimensions
    final_features = manual_features if manual_features is not None else recognition_result.features
    final_characteristics = manual_characteristics if manual_characteristics is not None else recognition_result.characteristics

    requested_size = sum(len(payload["data"]) for payload in image_payloads)

    # Fast fail quota check (authoritative check is the conditional UPDATE below)
    if current_user.storage_used_bytes + requested_size > current_user.storage_quota_bytes:
        available = current_user.storage_quota_bytes - current_user.storage_used_bytes
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Storage quota exceeded",
                "quota_bytes": current_user.storage_quota_bytes,
                "used_bytes": current_user.storage_used_bytes,
                "available_bytes": available,
                "requested_bytes": requested_size,
            },
        )

    # Generate product ID
    product_id = str(uuid4())

    # Reserve quota atomically (prevents concurrent uploads exceeding quota)
    reserve_stmt = (
        update(User)
        .where(User.id == current_user.id)
        .where(User.storage_used_bytes + requested_size <= User.storage_quota_bytes)
        .values(storage_used_bytes=User.storage_used_bytes + requested_size)
    )
    reserve_result = await db.execute(reserve_stmt)
    if (reserve_result.rowcount or 0) != 1:
        await db.rollback()
        fresh_user = await db.get(User, current_user.id)
        if fresh_user:
            quota = fresh_user.storage_quota_bytes
            used = fresh_user.storage_used_bytes
        else:
            quota = current_user.storage_quota_bytes
            used = current_user.storage_used_bytes
        available = max(0, quota - used)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Storage quota exceeded",
                "quota_bytes": quota,
                "used_bytes": used,
                "available_bytes": available,
                "requested_bytes": requested_size,
            },
        )

    primary_image_url = None
    saved_image_urls: List[str] = []
    product_images: List[ProductImage] = []
    total_image_size = 0

    # Save images to file system
    try:
        for idx, payload in enumerate(image_payloads):
            image_id = str(uuid4())
            is_primary = idx == primary_index
            image_url, image_size = save_product_image(
                user_id=current_user.id,
                product_id=product_id,
                image_data=payload["data"],
                original_format=payload["format"],
                image_id=None if is_primary else image_id,
            )
            if is_primary:
                primary_image_url = image_url
            saved_image_urls.append(image_url)
            total_image_size += image_size
            product_image = ProductImage(
                id=image_id,
                product_id=product_id,
                user_id=current_user.id,
                image_url=image_url,
                image_size_bytes=image_size,
                is_primary=is_primary,
            )
            product_images.append(product_image)
            db.add(product_image)
    except ProductStorageError as e:
        await db.rollback()
        for url in saved_image_urls:
            try:
                delete_product_image(url)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save product image: {str(e)}"
        )
    except Exception:
        await db.rollback()
        for url in saved_image_urls:
            try:
                delete_product_image(url)
            except Exception:
                pass
        raise

    # Create product record
    product = Product(
        id=product_id,
        user_id=current_user.id,
        name=final_name,
        dimensions=final_dimensions,
        features=final_features,
        characteristics=final_characteristics,
        original_image_url=primary_image_url or saved_image_urls[0],
        recognition_confidence=ai_confidence,
        recognition_metadata=recognition_metadata,
        image_size_bytes=total_image_size,
    )

    db.add(product)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        try:
            delete_product_image(image_url)
        except Exception:
            pass
        raise

    await db.refresh(product)

    images_stmt = (
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.is_primary.desc(), ProductImage.created_at.asc())
    )
    images_result = await db.execute(images_stmt)
    product_images = images_result.scalars().all()

    return build_product_detail_response(product, product_images)


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

    # Build query filters
    conditions = []
    if not current_user.is_admin:
        conditions.append(Product.user_id == current_user.id)

    # Apply name filter if provided
    if name:
        conditions.append(Product.name.ilike(f"%{name}%"))

    base_query = select(Product).where(*conditions)

    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    image_count_subq = (
        select(ProductImage.product_id, func.count(ProductImage.id).label("image_count"))
        .group_by(ProductImage.product_id)
        .subquery()
    )

    # Apply pagination and ordering
    list_query = (
        select(Product, image_count_subq.c.image_count)
        .outerjoin(image_count_subq, Product.id == image_count_subq.c.product_id)
        .where(*conditions)
        .order_by(Product.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    # Execute query
    result = await db.execute(list_query)
    rows = result.all()

    products_payload = []
    for product, image_count in rows:
        data = ProductSummary.model_validate(product).model_dump()
        count_value = image_count or 0
        if count_value == 0:
            count_value = 1
        data["image_count"] = count_value
        products_payload.append(ProductSummary(**data))

    return ProductListResponse(
        products=products_payload,
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
    stmt = select(Product).where(Product.id == product_id)
    if not current_user.is_admin:
        stmt = stmt.where(Product.user_id == current_user.id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        # Return 404 for non-existent or other user's products (security)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    images_stmt = (
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.is_primary.desc(), ProductImage.created_at.asc())
    )
    images_result = await db.execute(images_stmt)
    product_images = images_result.scalars().all()

    return build_product_detail_response(product, product_images)


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
    stmt = select(Product).where(Product.id == product_id)
    if not current_user.is_admin:
        stmt = stmt.where(Product.user_id == current_user.id)
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

    images_stmt = (
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.is_primary.desc(), ProductImage.created_at.asc())
    )
    images_result = await db.execute(images_stmt)
    product_images = images_result.scalars().all()

    return build_product_detail_response(product, product_images)


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
    stmt = select(Product).where(Product.id == product_id)
    if not current_user.is_admin:
        stmt = stmt.where(Product.user_id == current_user.id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    images_stmt = select(ProductImage).where(ProductImage.product_id == product_id)
    images_result = await db.execute(images_stmt)
    product_images = images_result.scalars().all()

    if product_images:
        for image in product_images:
            try:
                delete_product_image(image.image_url)
            except ProductStorageError:
                pass
        await db.execute(delete(ProductImage).where(ProductImage.product_id == product_id))
    else:
        try:
            delete_product_image(product.original_image_url)
        except ProductStorageError:
            pass

    # Reclaim storage quota
    stmt = (
        update(User)
        .where(User.id == product.user_id)
        .values(storage_used_bytes=User.storage_used_bytes - product.image_size_bytes)
    )
    await db.execute(stmt)

    # Delete product record
    await db.delete(product)
    await db.commit()

    return None
