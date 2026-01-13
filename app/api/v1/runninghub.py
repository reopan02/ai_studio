from __future__ import annotations

import logging
from typing import Any, Literal, Optional
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from app.api.deps import AuthContext, get_current_user
from app.clients.runninghub_client import RunningHubClient
from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _is_http_url(value: str) -> bool:
    try:
        parsed = urlparse(str(value or "").strip())
    except Exception:
        return False
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


class RunningHubImageToVideoRealisticRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt: str = Field(min_length=1, title="提示词")
    resolution: Literal["720p", "1080p"] = Field(default="1080p", title="分辨率")
    aspect_ratio: Literal["16:9", "9:16"] = Field(default="16:9", alias="aspectRatio", title="比例")
    image_url: str = Field(alias="imageUrl", title="图片地址")
    duration: Literal[4, 8, 12] = Field(default=4, title="视频时长(秒)")


class RunningHubResultItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    url: str
    output_type: str = Field(alias="outputType")


class RunningHubTaskSubmitResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias="taskId")
    status: str
    error_code: Optional[str] = Field(default=None, alias="errorCode")
    error_message: Optional[str] = Field(default=None, alias="errorMessage")
    results: Optional[list[RunningHubResultItem]] = Field(default=None)
    client_id: Optional[str] = Field(default=None, alias="clientId")
    prompt_tips: Optional[str] = Field(default=None, alias="promptTips")


@router.post("/runninghub/image-to-video-realistic", response_model=RunningHubTaskSubmitResult)
async def runninghub_image_to_video_realistic(
    payload: RunningHubImageToVideoRealisticRequest,
    x_runninghub_token: Optional[str] = Header(default=None),
    auth: AuthContext = Depends(get_current_user),
):
    if not _is_http_url(payload.image_url):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="imageUrl must be a valid http(s) URL")

    settings = get_settings()
    token = str(x_runninghub_token or settings.RUNNINGHUB_API_KEY or "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RUNNINGHUB_API_KEY is not configured (set env or pass X-RunningHub-Token header)",
        )

    try:
        async with RunningHubClient(token=token, base_url=settings.RUNNINGHUB_BASE_URL) as client:
            response_json: dict[str, Any] = await client.image_to_video_realistic(
                prompt=payload.prompt,
                resolution=payload.resolution,
                aspect_ratio=payload.aspect_ratio,
                image_url=payload.image_url,
                duration=payload.duration,
            )
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
    except Exception as exc:
        logger.exception("RunningHub request failed for user_id=%s", auth.user_id)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    try:
        return RunningHubTaskSubmitResult.model_validate(response_json)
    except Exception:
        logger.exception("Failed to validate RunningHub response payload")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid RunningHub response format")
