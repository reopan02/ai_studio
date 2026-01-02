from __future__ import annotations

import json
import logging
from typing import Any, Optional
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.api.deps import get_current_user
from app.clients.image_edits_client import ImageEditsClient
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


def _extract_first_image_url(response_json: Any) -> str | None:
    if not isinstance(response_json, dict):
        return None

    direct = response_json.get("url")
    if isinstance(direct, str) and _is_http_url(direct):
        return direct

    data = response_json.get("data")
    if isinstance(data, list) and data and isinstance(data[0], dict):
        url = data[0].get("url")
        if isinstance(url, str) and _is_http_url(url):
            return url
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
        title=title,
        model=str(model),
        prompt=str(prompt),
        status="completed",
        image_url=_extract_first_image_url(provider_response),
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
    response_format: Optional[str] = Form(default=None),
    title: Optional[str] = Form(default=None),
    x_api_key: Optional[str] = Header(default=None),
    x_base_url: Optional[str] = Header(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Text-to-image generation endpoint following OpenAI DALL-E format."""
    # Validate inputs
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt is required")
    if len(prompt) > 1000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt must not exceed 1000 characters")
    n = max(1, min(10, n))
    valid_sizes = {"256x256", "512x512", "1024x1024"}
    if size and size not in valid_sizes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid size. Must be one of: {', '.join(valid_sizes)}")

    settings = get_settings()
    api_key = (x_api_key or settings.API_KEY or "").strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API_KEY is not configured")

    base_url = (x_base_url or settings.API_BASE_URL or "").strip() or None

    try:
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
        "response_format": response_format,
        "provider": {"base_url": base_url or settings.API_BASE_URL},
    }
    response_dict: dict[str, Any] = provider_response if isinstance(provider_response, dict) else {"raw": provider_response}

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
        title=title,
        model=str(model),
        prompt=str(prompt),
        status="completed",
        image_url=_extract_first_image_url(provider_response),
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
