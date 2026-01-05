from __future__ import annotations

import base64
import json
import logging
from typing import Any, Optional
from urllib.parse import urlparse
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.api.deps import get_current_user
from app.clients.image_edits_client import ImageEditsClient
from app.clients.gemini_image_client import GeminiImageClient
from app.config import get_settings
from app.core.encryption import EncryptionError, decrypt_for_user, encrypt_for_user
from app.db.session import get_db
from app.models.database import User, UserImage
from app.models.schemas import UserImageCreate, UserImageDetail, UserImageSummary, UserImageUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


def _json_dumps(data: Any) -> bytes:
    return json.dumps(data, default=str, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _json_loads(payload: bytes) -> Any:
    return json.loads(payload.decode("utf-8"))


def _ensure_owner(image: UserImage, user: User) -> None:
    if user.is_admin:
        return
    if image.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


def _is_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except Exception:
        return False
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


def _count_images_in_response(response_json: Any) -> int:
    """Count the number of images in the response."""
    if not isinstance(response_json, dict):
        return 0

    count = 0

    # Check for direct b64_json
    if response_json.get("b64_json"):
        count += 1

    # Check in data array
    data = response_json.get("data")
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("b64_json"):
                count += 1

    return count


def _build_image_api_url(image_id: str, index: int = 0) -> str:
    """Build API URL to access image data from database.

    Args:
        image_id: Image record ID
        index: Index for multiple images in one response

    Returns:
        API endpoint URL to fetch image data
    """
    return f"/api/v1/images/{image_id}/data/{index}"


def _extract_first_image_url(response_json: Any, image_id: str) -> str | None:
    """Build API URL for accessing stored image data.

    Args:
        response_json: The API response JSON (to check if images exist)
        image_id: Image record ID for building API URL

    Returns:
        API endpoint URL to fetch image data, or None if no images
    """
    if not isinstance(response_json, dict):
        return None

    # Check if there are any images in the response
    has_images = False

    # Check for direct b64_json
    if response_json.get("b64_json"):
        has_images = True

    # Check in data array
    data = response_json.get("data")
    if isinstance(data, list) and data:
        for item in data:
            if isinstance(item, dict) and item.get("b64_json"):
                has_images = True
                break

    if has_images:
        return _build_image_api_url(image_id, 0)

    return None


@router.post("/images/edits", response_model=UserImageDetail, status_code=status.HTTP_201_CREATED)
async def images_edits_and_store(
    model: str = Form(...),
    prompt: str = Form(...),
    response_format: Optional[str] = Form(default=None),
    aspect_ratio: Optional[str] = Form(default=None),
    image_size: Optional[str] = Form(default=None),
    title: Optional[str] = Form(default=None),
    image: list[UploadFile] = File(default=[]),
    x_api_key: Optional[str] = Header(default=None),
    x_base_url: Optional[str] = Header(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    api_key = (x_api_key or settings.API_KEY or "").strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API_KEY is not configured")

    base_url = (x_base_url or settings.API_BASE_URL or "").strip() or None

    try:
        provider_images: list[tuple[str, bytes, str]] = []
        for f in image:
            content = await f.read()
            if not content:
                continue
            provider_images.append((f.filename or "image.png", content, f.content_type or "application/octet-stream"))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to read uploaded files: {exc}")

    try:
        # Use GeminiImageClient for Gemini models
        if GeminiImageClient.is_gemini_model(model):
            async with GeminiImageClient(api_key=api_key, base_url=base_url) as client:
                provider_response = await client.generate_image(
                    model=model,
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                    images=provider_images,
                )
        else:
            async with ImageEditsClient(api_key=api_key, base_url=base_url) as client:
                provider_response = await client.images_edits(
                    model=model,
                    prompt=prompt,
                    response_format=response_format,
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                    images=provider_images,
                )
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    request_dict = {
        "model": model,
        "prompt": prompt,
        "response_format": response_format,
        "aspect_ratio": aspect_ratio,
        "image_size": image_size,
        "images": [{"filename": n, "content_type": ct, "size_bytes": len(b)} for n, b, ct in provider_images],
        "provider": {"base_url": base_url or settings.API_BASE_URL},
    }
    response_dict: dict[str, Any] = provider_response if isinstance(provider_response, dict) else {"raw": provider_response}

    # Generate image ID first so we can build API URLs
    image_id = str(uuid4())

    # Build image URL from response
    image_url = _extract_first_image_url(response_dict, image_id)
    logger.info("Generated (edits) image_id=%s, image_url=%s, response_keys=%s",
                image_id, image_url, list(response_dict.keys()) if isinstance(response_dict, dict) else None)

    try:
        request_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(request_dict))
        response_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(response_dict))
    except EncryptionError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    size_bytes = len(request_blob) + len(response_blob)
    if user.storage_used_bytes + size_bytes > user.storage_quota_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Storage quota exceeded")

    record = UserImage(
        id=image_id,
        user_id=user.id,
        title=title,
        model=str(model),
        prompt=str(prompt),
        status="completed",
        image_url=image_url,
        request_encrypted=request_blob,
        response_encrypted=response_blob,
        size_bytes=size_bytes,
    )

    try:
        user.storage_used_bytes += size_bytes
        db.add(record)
        db.add(user)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to persist generated image for user_id=%s", user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save image record")

    await db.refresh(record)
    return UserImageDetail(
        **UserImageSummary.model_validate(record).model_dump(),
        request=request_dict,
        response=response_dict,
    )


@router.post("/images/generations", response_model=UserImageDetail, status_code=status.HTTP_201_CREATED)
async def images_generations_and_store(
    model: str = Form(...),
    prompt: str = Form(...),
    n: int = Form(default=1),
    size: Optional[str] = Form(default=None),
    aspect_ratio: Optional[str] = Form(default=None),
    response_format: Optional[str] = Form(default=None),
    title: Optional[str] = Form(default=None),
    x_api_key: Optional[str] = Header(default=None),
    x_base_url: Optional[str] = Header(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Text-to-image generation endpoint supporting Gemini and legacy formats."""
    # Validate inputs
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt is required")
    if len(prompt) > 1000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt must not exceed 1000 characters")
    n = max(1, min(10, n))
    # Support both Gemini format (1K, 2K, 4K) and legacy pixel format
    valid_sizes = {"1K", "2K", "4K", "256x256", "512x512", "1024x1024"}
    if size and size not in valid_sizes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid size. Must be one of: {', '.join(sorted(valid_sizes))}")

    settings = get_settings()
    api_key = (x_api_key or settings.API_KEY or "").strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API_KEY is not configured")

    base_url = (x_base_url or settings.API_BASE_URL or "").strip() or None

    try:
        # Use GeminiImageClient for Gemini models
        if GeminiImageClient.is_gemini_model(model):
            async with GeminiImageClient(api_key=api_key, base_url=base_url) as client:
                provider_response = await client.generate_image(
                    model=model,
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    image_size=size,  # size maps to image_size for Gemini
                )
        else:
            async with ImageEditsClient(api_key=api_key, base_url=base_url) as client:
                provider_response = await client.images_generations(
                    model=model,
                    prompt=prompt,
                    n=n,
                    size=size,
                    response_format=response_format,
                )
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    request_dict = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
        "aspect_ratio": aspect_ratio,
        "response_format": response_format,
        "provider": {"base_url": base_url or settings.API_BASE_URL},
    }
    response_dict: dict[str, Any] = provider_response if isinstance(provider_response, dict) else {"raw": provider_response}

    # Generate image ID first so we can build API URLs
    image_id = str(uuid4())

    # Build image URL from response
    image_url = _extract_first_image_url(response_dict, image_id)
    logger.info("Generated image_id=%s, image_url=%s, response_keys=%s",
                image_id, image_url, list(response_dict.keys()) if isinstance(response_dict, dict) else None)

    try:
        request_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(request_dict))
        response_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(response_dict))
    except EncryptionError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    size_bytes = len(request_blob) + len(response_blob)
    if user.storage_used_bytes + size_bytes > user.storage_quota_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Storage quota exceeded")

    record = UserImage(
        id=image_id,
        user_id=user.id,
        title=title,
        model=str(model),
        prompt=str(prompt),
        status="completed",
        image_url=image_url,
        request_encrypted=request_blob,
        response_encrypted=response_blob,
        size_bytes=size_bytes,
    )

    try:
        user.storage_used_bytes += size_bytes
        db.add(record)
        db.add(user)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to persist generated image for user_id=%s", user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save image record")

    await db.refresh(record)
    return UserImageDetail(
        **UserImageSummary.model_validate(record).model_dump(),
        request=request_dict,
        response=response_dict,
    )


@router.get("/images", response_model=list[UserImageSummary])
async def list_images(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    limit = max(1, min(200, int(limit)))
    offset = max(0, int(offset))

    stmt = select(UserImage).options(
        load_only(
            UserImage.id,
            UserImage.user_id,
            UserImage.title,
            UserImage.model,
            UserImage.prompt,
            UserImage.status,
            UserImage.image_url,
            UserImage.size_bytes,
            UserImage.created_at,
            UserImage.updated_at,
        )
    )
    if not user.is_admin:
        stmt = stmt.where(UserImage.user_id == user.id)
    stmt = stmt.order_by(desc(UserImage.created_at)).offset(offset).limit(limit)
    items = (await db.execute(stmt)).scalars().all()
    return items


@router.get("/images/{image_id}", response_model=UserImageDetail)
async def get_image(
    image_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = await db.get(UserImage, image_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    _ensure_owner(record, user)

    try:
        request_payload = decrypt_for_user(user_id=record.user_id, blob=record.request_encrypted)
        response_payload = decrypt_for_user(user_id=record.user_id, blob=record.response_encrypted)
    except EncryptionError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return UserImageDetail(
        **UserImageSummary.model_validate(record).model_dump(),
        request=_json_loads(request_payload),
        response=_json_loads(response_payload),
    )


@router.get("/images/{image_id}/data/{index}")
async def get_image_data(
    image_id: str,
    index: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get raw image data from encrypted database storage.

    Decodes base64 image data from the encrypted response and returns as binary.
    """
    record = await db.get(UserImage, image_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    _ensure_owner(record, user)

    # Decode from encrypted response
    try:
        response_payload = decrypt_for_user(user_id=record.user_id, blob=record.response_encrypted)
        response_data = _json_loads(response_payload)
    except EncryptionError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    # Extract base64 data
    b64_data: str | None = None

    if isinstance(response_data, dict):
        data_array = response_data.get("data")
        if isinstance(data_array, list) and index < len(data_array):
            item = data_array[index]
            if isinstance(item, dict):
                b64_data = item.get("b64_json")

        if not b64_data and index == 0:
            b64_data = response_data.get("b64_json")

    if not b64_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image data not found")

    try:
        image_bytes = base64.b64decode(b64_data)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to decode image")

    # Detect content type
    content_type = "image/png"
    if image_bytes[:3] == b'\xff\xd8\xff':
        content_type = "image/jpeg"
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        content_type = "image/webp"
    elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        content_type = "image/gif"

    return Response(content=image_bytes, media_type=content_type)


@router.patch("/images/{image_id}", response_model=UserImageSummary)
async def update_image(
    image_id: str,
    payload: UserImageUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = await db.get(UserImage, image_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    _ensure_owner(record, user)

    if "title" in payload.model_fields_set:
        record.title = payload.title

    try:
        db.add(record)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to update image_id=%s for user_id=%s", image_id, user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update image record")
    await db.refresh(record)
    return record


@router.post("/images", response_model=UserImageSummary, status_code=status.HTTP_201_CREATED)
async def create_image_record(
    payload: UserImageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image_url = str(payload.image_url or "").strip() or None

    if image_url and len(image_url) <= 1000:
        existing = (
            await db.execute(
                select(UserImage).where(
                    UserImage.user_id == user.id,
                    UserImage.image_url == image_url,
                )
            )
        ).scalars().first()
        if existing:
            return existing

    request_dict = payload.request or {
        "model": payload.model,
        "prompt": payload.prompt,
        "metadata": payload.metadata,
    }
    response_dict = payload.response or {
        "image_url": payload.image_url,
        "status": payload.status,
    }

    try:
        request_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(request_dict))
        response_blob = encrypt_for_user(user_id=user.id, plaintext=_json_dumps(response_dict))
    except EncryptionError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    size_bytes = len(request_blob) + len(response_blob)
    if user.storage_used_bytes + size_bytes > user.storage_quota_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Storage quota exceeded")

    record = UserImage(
        user_id=user.id,
        title=payload.title,
        model=payload.model,
        prompt=payload.prompt,
        status=payload.status,
        image_url=image_url if image_url and len(image_url) <= 1000 and _is_http_url(image_url) else None,
        request_encrypted=request_blob,
        response_encrypted=response_blob,
        size_bytes=size_bytes,
    )

    try:
        user.storage_used_bytes += size_bytes
        db.add(record)
        db.add(user)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to persist image record for user_id=%s", user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save image record")

    await db.refresh(record)
    return record


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = await db.get(UserImage, image_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    _ensure_owner(record, user)

    try:
        owner = await db.get(User, record.user_id)
        if owner:
            owner.storage_used_bytes = max(0, int(owner.storage_used_bytes) - int(record.size_bytes or 0))
            db.add(owner)
        await db.delete(record)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to delete image_id=%s for user_id=%s", image_id, user.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete image record")
    return None
