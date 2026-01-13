from __future__ import annotations

from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel

from app.api.deps import AuthContext, get_current_user
from app.config import get_settings
from app.core.product_storage import ProductStorageError, delete_product_image, get_image_format, save_product_image

router = APIRouter()


def _is_own_product_image_url(image_url: str, user_id: str) -> bool:
    value = str(image_url or "").strip()
    if not value:
        return False

    if value.startswith("/static/"):
        value = value[len("/static") :]

    prefix = f"/uploads/products/{user_id}/"
    return value.startswith(prefix)


class ProductImageUploadItem(BaseModel):
    image_url: str
    is_primary: bool
    image_size_bytes: int


class ProductImageUploadResponse(BaseModel):
    product_id: str
    images: list[ProductImageUploadItem]


class ProductImageDeleteRequest(BaseModel):
    image_url: str


class ProductImageDeleteResponse(BaseModel):
    deleted: bool


class RunningHubImageUploadResponse(BaseModel):
    image_url: str
    relative_url: str
    image_size_bytes: int


@router.post("/uploads/products", response_model=ProductImageUploadResponse)
async def upload_product_images(
    product_id: str = Form(...),
    primary_index: int = Form(default=0),
    images: list[UploadFile] = File(...),
    auth: AuthContext = Depends(get_current_user),
):
    if not images:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one image file is required")

    if primary_index < 0 or primary_index >= len(images):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="primary_index is out of range")

    saved: list[ProductImageUploadItem] = []
    saved_urls: list[str] = []

    try:
        for idx, upload in enumerate(images):
            raw = await upload.read()
            if not raw:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Empty image file at index {idx}")

            try:
                detected_format = get_image_format(raw)
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

            is_primary = idx == primary_index
            image_id: Optional[str] = None if is_primary else str(uuid4())
            image_url, image_size = save_product_image(
                user_id=auth.user_id,
                product_id=product_id,
                image_data=raw,
                original_format=img_format,
                image_id=image_id,
            )
            saved_urls.append(image_url)
            saved.append(ProductImageUploadItem(image_url=image_url, is_primary=is_primary, image_size_bytes=image_size))

        return ProductImageUploadResponse(product_id=product_id, images=saved)
    except HTTPException:
        # Cleanup files we already wrote.
        for url in saved_urls:
            try:
                delete_product_image(url)
            except Exception:
                pass
        raise
    except Exception as exc:
        for url in saved_urls:
            try:
                delete_product_image(url)
            except Exception:
                pass
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/uploads/products/delete", response_model=ProductImageDeleteResponse)
async def delete_product_image_upload(
    payload: ProductImageDeleteRequest,
    auth: AuthContext = Depends(get_current_user),
):
    image_url = str(payload.image_url or "").strip()
    if not _is_own_product_image_url(image_url, auth.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    try:
        deleted = bool(delete_product_image(image_url))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return ProductImageDeleteResponse(deleted=deleted)


@router.post("/uploads/runninghub/image", response_model=RunningHubImageUploadResponse)
async def upload_runninghub_image(
    request: Request,
    image: UploadFile = File(...),
    auth: AuthContext = Depends(get_current_user),
):
    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty image file")

    try:
        detected_format = get_image_format(raw)
    except ProductStorageError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid or unsupported image file")

    if detected_format not in {"jpeg", "jpg", "png"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only JPEG and PNG images are supported")

    ext = "png" if detected_format == "png" else "jpg"
    filename = f"{uuid4()}.{ext}"

    settings = get_settings()
    upload_url = settings.UPLOAD_URL
    upload_apikey = settings.UPLOAD_APIKEY

    if upload_url and upload_apikey:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {"file": (filename, raw, f"image/{ext}")}
                headers = {"Authorization": f"Bearer {upload_apikey}"}
                resp = await client.post(upload_url, files=files, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                public_url = data.get("url", "")
                if not public_url:
                    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Upload API did not return url")
                return RunningHubImageUploadResponse(
                    image_url=public_url,
                    relative_url="",
                    image_size_bytes=len(raw),
                )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Upload failed: {exc.response.text}")
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Upload failed: {exc}")

    user_dir = Path("app/static/uploads/runninghub") / auth.user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / filename
    file_path.write_bytes(raw)

    relative_url = f"/uploads/runninghub/{auth.user_id}/{filename}"
    base = str(request.base_url).rstrip("/")
    public_url = f"{base}{relative_url}"

    return RunningHubImageUploadResponse(
        image_url=public_url,
        relative_url=relative_url,
        image_size_bytes=len(raw),
    )
