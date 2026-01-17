from __future__ import annotations

import io
from typing import AsyncIterator, Literal, Optional

import httpx
from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import get_settings

router = APIRouter()

VideoModel = Literal["sora-2", "sora-2-pro"]
VideoSeconds = Literal["4", "8", "12"]
VideoSize = Literal["1280x720", "720x1280", "1024x1792", "1792x1024"]

_SORA2_SIZES: set[str] = {"1280x720", "720x1280"}
_SORA2_PRO_SIZES: set[str] = {"1280x720", "720x1280", "1024x1792", "1792x1024"}


def _normalize_authorization(authorization: str | None) -> str:
    value = str(authorization or "").strip()
    if not value:
        settings = get_settings()
        api_key = str(settings.VIDEO_GEN_API_KEY or "").strip()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="VIDEO_GEN_API_KEY is not configured",
            )
        return f"Bearer {api_key}"

    parts = value.split(None, 1)
    if len(parts) == 1:
        return f"Bearer {value}"
    if parts[0].lower() == "bearer" and parts[1].strip():
        return value
    return value


def _upstream_url(path: str) -> str:
    settings = get_settings()
    base_url = str(settings.VIDEO_GEN_API_BASE_URL or "").strip().rstrip("/")
    if not base_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="VIDEO_GEN_API_BASE_URL is not configured",
        )
    normalized_path = str(path or "").strip()
    if not normalized_path.startswith("/"):
        normalized_path = "/" + normalized_path
    return f"{base_url}{normalized_path}"


def _proxy_response(upstream: httpx.Response) -> Response:
    media_type = upstream.headers.get("content-type") or None
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=media_type,
    )


def _parse_video_size(value: str) -> tuple[int, int]:
    raw = str(value or "").strip()
    parts = raw.lower().split("x")
    if len(parts) != 2:
        raise ValueError("size 格式必须为 {width}x{height}")
    w = int(parts[0])
    h = int(parts[1])
    if w <= 0 or h <= 0:
        raise ValueError("size 必须为正整数")
    return w, h


def _prepare_reference_image(blob: bytes, *, target_w: int, target_h: int) -> tuple[bytes, str]:
    """
    Upstream requires `input_reference` to exactly match requested width/height.

    - Apply EXIF orientation
    - Center-crop to preserve aspect ratio
    - Resize to exact target size
    - Encode as PNG for broad compatibility
    """
    try:
        with Image.open(io.BytesIO(blob)) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode not in {"RGB", "RGBA"}:
                img = img.convert("RGB")
            resized = ImageOps.fit(img, (target_w, target_h), method=Image.Resampling.LANCZOS)
            out = io.BytesIO()
            resized.save(out, format="PNG")
            return out.getvalue(), "image/png"
    except UnidentifiedImageError as exc:
        raise ValueError("input_reference 不是有效的图片文件") from exc


@router.post("/videos")
async def create_video(
    prompt: str = Form(...),
    model: VideoModel = Form(...),
    seconds: VideoSeconds = Form(default="4"),
    size: VideoSize = Form(default="720x1280"),
    input_reference: Optional[UploadFile] = File(default=None),
    authorization: Optional[str] = Header(default=None),
):
    settings = get_settings()
    url = _upstream_url("/v1/videos")
    headers = {"Authorization": _normalize_authorization(authorization)}

    if model == "sora-2" and size not in _SORA2_SIZES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="size 对于 sora-2 仅支持 1280x720 / 720x1280",
        )
    if model == "sora-2-pro" and size not in _SORA2_PRO_SIZES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="size 对于 sora-2-pro 仅支持 1280x720 / 720x1280 / 1024x1792 / 1792x1024",
        )

    multipart: dict[str, tuple[None, str] | tuple[str, bytes, str]] = {
        "prompt": (None, prompt),
        "model": (None, model),
        "seconds": (None, seconds),
        "size": (None, size),
    }
    if input_reference is not None:
        blob = await input_reference.read()
        if blob:
            try:
                target_w, target_h = _parse_video_size(size)
                prepared, mime = _prepare_reference_image(blob, target_w=target_w, target_h=target_h)
            except ValueError as exc:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

            multipart["input_reference"] = ("input_reference.png", prepared, mime)

    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            upstream = await client.post(url, files=multipart, headers=headers)
        return _proxy_response(upstream)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/videos/{video_id}")
async def get_video_status(
    video_id: str,
    authorization: Optional[str] = Header(default=None),
):
    settings = get_settings()
    url = _upstream_url(f"/v1/videos/{video_id}")
    headers = {"Authorization": _normalize_authorization(authorization)}

    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            upstream = await client.get(url, headers=headers)
        return _proxy_response(upstream)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/videos/{video_id}/content")
async def get_video_content(
    video_id: str,
    authorization: Optional[str] = Header(default=None),
):
    settings = get_settings()
    url = _upstream_url(f"/v1/videos/{video_id}/content")
    headers = {"Authorization": _normalize_authorization(authorization)}

    client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT, headers=headers)
    request = client.build_request("GET", url)

    try:
        upstream = await client.send(request, stream=True)
    except httpx.HTTPError as exc:
        await client.aclose()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    if upstream.status_code >= 400:
        body = await upstream.aread()
        await upstream.aclose()
        await client.aclose()
        media_type = upstream.headers.get("content-type") or None
        return Response(content=body, status_code=upstream.status_code, media_type=media_type)

    media_type = upstream.headers.get("content-type") or None

    async def _aiter() -> AsyncIterator[bytes]:
        try:
            async for chunk in upstream.aiter_bytes():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(_aiter(), status_code=upstream.status_code, media_type=media_type)
