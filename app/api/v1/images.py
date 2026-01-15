from __future__ import annotations

import asyncio
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


def _extract_first_openai_image_data_item(response_json: Any) -> dict[str, Any] | None:
    if not isinstance(response_json, dict):
        return None

    data = response_json.get("data")
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue

            url = item.get("url")
            if isinstance(url, str) and url:
                return item

            b64_json = item.get("b64_json")
            if isinstance(b64_json, str) and b64_json:
                return item

            image_url = item.get("image_url") or item.get("imageUrl")
            if isinstance(image_url, str) and image_url:
                return {"url": image_url}

    url = response_json.get("url") or response_json.get("image_url") or response_json.get("imageUrl")
    if isinstance(url, str) and url:
        return {"url": url}

    b64_json = response_json.get("b64_json") or response_json.get("b64Json")
    if isinstance(b64_json, str) and b64_json:
        return {"b64_json": b64_json}

    return None


def _aggregate_openai_image_responses(responses: list[Any], *, expected_count: int) -> dict[str, Any]:
    data: list[dict[str, Any]] = []
    for idx, response in enumerate(responses, start=1):
        item = _extract_first_openai_image_data_item(response)
        if not item:
            raise RuntimeError(f"Upstream response #{idx} did not contain any image data")
        data.append(item)

    if len(data) != expected_count:
        raise RuntimeError(f"Expected {expected_count} images but got {len(data)}")

    return {"data": data}


@router.post("/images/edits", response_model=UserImageDetail, status_code=status.HTTP_201_CREATED)
async def images_edits_and_store(
    model: str = Form(...),
    prompt: str = Form(...),
    n: int = Form(default=1),
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
    n = max(1, min(10, n))
    is_gemini = GeminiImageClient.is_gemini_model(model)

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
        provider_responses: list[Any] = []

        if is_gemini:
            async with GeminiImageClient(api_key=api_key, base_url=base_url) as client:
                calls = [
                    client.generate_image(
                        model=model,
                        prompt=prompt,
                        aspect_ratio=aspect_ratio,
                        image_size=image_size,
                        images=provider_images,
                    )
                    for _ in range(n)
                ]
                provider_responses = await asyncio.gather(*calls)
        else:
            async with ImageEditsClient(api_key=api_key, base_url=base_url) as client:
                calls = [
                    client.images_edits(
                        model=model,
                        prompt=prompt,
                        response_format=response_format,
                        aspect_ratio=aspect_ratio,
                        image_size=image_size,
                        images=provider_images,
                    )
                    for _ in range(n)
                ]
                provider_responses = await asyncio.gather(*calls)

        provider_response = _aggregate_openai_image_responses(provider_responses, expected_count=n)
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    image_meta = [
        {"filename": filename, "content_type": content_type, "size_bytes": len(blob)}
        for filename, blob, content_type in provider_images
    ]
    if is_gemini:
        provider_request_endpoint = f"/v1beta/models/{model}:generateContent"
        provider_request_payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        }
        # Build imageConfig per API spec (banana.md)
        image_config: dict[str, Any] = {}
        if aspect_ratio:
            image_config["aspectRatio"] = aspect_ratio
        if image_size:
            normalized_size = image_size.upper()
            if normalized_size in ("2K", "4K"):
                image_config["imageSize"] = normalized_size
        if image_config:
            provider_request_payload["generationConfig"]["imageConfig"] = image_config
        if image_meta:
            provider_request_payload["images"] = image_meta
    else:
        provider_request_endpoint = "/v1/images/edits"
        provider_request_payload = {
            "model": model,
            "prompt": prompt,
            "images": image_meta,
        }
        if response_format:
            provider_request_payload["response_format"] = response_format
        if aspect_ratio:
            provider_request_payload["aspect_ratio"] = aspect_ratio
        if image_size:
            provider_request_payload["image_size"] = image_size

    request_dict = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "response_format": response_format,
        "aspect_ratio": aspect_ratio,
        "image_size": image_size,
        "images": image_meta,
        "provider": {
            "base_url": base_url or settings.API_BASE_URL,
            "requests": {
                "count": n,
                "endpoint": provider_request_endpoint,
                "payload": provider_request_payload,
            },
        },
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
    is_gemini = GeminiImageClient.is_gemini_model(model)

    try:
        provider_responses: list[Any] = []

        # Use GeminiImageClient for Gemini models
        if is_gemini:
            async with GeminiImageClient(api_key=api_key, base_url=base_url) as client:
                calls = [
                    client.generate_image(
                        model=model,
                        prompt=prompt,
                        aspect_ratio=aspect_ratio,
                        image_size=size,  # size maps to image_size for Gemini
                    )
                    for _ in range(n)
                ]
                provider_responses = await asyncio.gather(*calls)
        else:
            async with ImageEditsClient(api_key=api_key, base_url=base_url) as client:
                # Some upstream providers reject the `n` parameter. Treat `n` as
                # concurrency and issue single-image requests.
                calls = [
                    client.images_generations(
                        model=model,
                        prompt=prompt,
                        size=size,
                        response_format=response_format,
                    )
                    for _ in range(n)
                ]
                provider_responses = await asyncio.gather(*calls)

        provider_response = _aggregate_openai_image_responses(provider_responses, expected_count=n)
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    if is_gemini:
        provider_request_endpoint = f"/v1beta/models/{model}:generateContent"
        provider_request_payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        }
        # Build imageConfig per API spec (banana.md)
        image_config: dict[str, Any] = {}
        if aspect_ratio:
            image_config["aspectRatio"] = aspect_ratio
        if size:
            normalized_size = size.upper()
            if normalized_size in ("2K", "4K"):
                image_config["imageSize"] = normalized_size
        if image_config:
            provider_request_payload["generationConfig"]["imageConfig"] = image_config
    else:
        provider_request_endpoint = "/v1/images/generations"
        provider_request_payload = {"model": model, "prompt": prompt}
        if size:
            provider_request_payload["size"] = size
        if response_format:
            provider_request_payload["response_format"] = response_format

    request_dict = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
        "aspect_ratio": aspect_ratio,
        "response_format": response_format,
        "provider": {
            "base_url": base_url or settings.API_BASE_URL,
            "requests": {
                "count": n,
                "endpoint": provider_request_endpoint,
                "payload": provider_request_payload,
            },
        },
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
