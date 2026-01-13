from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status

from app.api.deps import AuthContext, get_current_user
from app.clients.gemini_image_client import GeminiImageClient
from app.clients.image_edits_client import ImageEditsClient
from app.config import get_settings

router = APIRouter()


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


def _extract_first_image_url(response_json: Any) -> str | None:
    if not isinstance(response_json, dict):
        return None

    direct = response_json.get("url")
    if isinstance(direct, str) and direct:
        return direct

    data = response_json.get("data")
    if isinstance(data, list) and data and isinstance(data[0], dict):
        url = data[0].get("url")
        if isinstance(url, str) and url:
            return url

        b64_json = data[0].get("b64_json")
        if isinstance(b64_json, str) and b64_json:
            return f"data:image/png;base64,{b64_json}"

    return None


@router.post("/images/edits")
async def images_edits(
    model: str = Form(...),
    prompt: str = Form(...),
    n: int = Form(default=1),
    response_format: Optional[str] = Form(default=None),
    aspect_ratio: Optional[str] = Form(default=None),
    image_size: Optional[str] = Form(default=None),
    image: list[UploadFile] = File(default=[]),
    x_api_key: Optional[str] = Header(default=None),
    x_base_url: Optional[str] = Header(default=None),
    _auth: AuthContext = Depends(get_current_user),
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

    request_dict = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "response_format": response_format,
        "aspect_ratio": aspect_ratio,
        "image_size": image_size,
        "images": [
            {"filename": filename, "content_type": content_type, "size_bytes": len(blob)}
            for filename, blob, content_type in provider_images
        ],
        "provider": {"base_url": base_url or settings.API_BASE_URL},
    }
    response_dict: dict[str, Any] = provider_response if isinstance(provider_response, dict) else {"raw": provider_response}

    return {"image_url": _extract_first_image_url(provider_response), "request": request_dict, "response": response_dict}


@router.post("/images/generations")
async def images_generations(
    model: str = Form(...),
    prompt: str = Form(...),
    n: int = Form(default=1),
    size: Optional[str] = Form(default=None),
    aspect_ratio: Optional[str] = Form(default=None),
    response_format: Optional[str] = Form(default=None),
    x_api_key: Optional[str] = Header(default=None),
    x_base_url: Optional[str] = Header(default=None),
    _auth: AuthContext = Depends(get_current_user),
):
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt is required")
    if len(prompt) > 1000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt must not exceed 1000 characters")

    n = max(1, min(10, n))
    valid_sizes = {"1K", "2K", "4K", "256x256", "512x512", "1024x1024"}
    if size and size not in valid_sizes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid size. Must be one of: {', '.join(sorted(valid_sizes))}",
        )

    settings = get_settings()
    api_key = (x_api_key or settings.API_KEY or "").strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API_KEY is not configured")

    base_url = (x_base_url or settings.API_BASE_URL or "").strip() or None
    is_gemini = GeminiImageClient.is_gemini_model(model)

    try:
        provider_responses: list[Any] = []

        if is_gemini:
            async with GeminiImageClient(api_key=api_key, base_url=base_url) as client:
                calls = [
                    client.generate_image(
                        model=model,
                        prompt=prompt,
                        aspect_ratio=aspect_ratio,
                        image_size=size,
                    )
                    for _ in range(n)
                ]
                provider_responses = await asyncio.gather(*calls)
        else:
            async with ImageEditsClient(api_key=api_key, base_url=base_url) as client:
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

    return {"image_url": _extract_first_image_url(provider_response), "request": request_dict, "response": response_dict}

