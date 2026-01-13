from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from starlette.background import BackgroundTask, BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_session_factory
from app.models.database import ApiRequestLog

_SENSITIVE_KEYS = {
    "password",
    "pass",
    "api_key",
    "authorization",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "video_base64",
    "image",
    "input_image_base64",
}


def _redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        redacted: Dict[str, Any] = {}
        for key, value in obj.items():
            if str(key).lower() in _SENSITIVE_KEYS:
                redacted[key] = "<redacted>"
            else:
                redacted[key] = _redact(value)
        return redacted
    if isinstance(obj, list):
        return [_redact(item) for item in obj]
    return obj


def _sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    redacted_headers: Dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in {"authorization", "cookie", "set-cookie", "x-api-key", "x-runninghub-token"}:
            continue
        redacted_headers[key] = value
    return redacted_headers


def _parse_body(body: bytes, content_type: str, max_bytes: int) -> Tuple[Optional[Any], Optional[str]]:
    if not body:
        return None, None

    if len(body) > max_bytes:
        return None, body[:max_bytes].decode("utf-8", errors="replace")

    if "application/json" in (content_type or ""):
        try:
            parsed = json.loads(body.decode("utf-8", errors="replace"))
            return _redact(parsed), None
        except Exception:
            return None, body.decode("utf-8", errors="replace")

    return None, body.decode("utf-8", errors="replace")


async def _resolve_auth_context(request: Request) -> Tuple[Optional[str], Optional[str]]:
    auth = request.headers.get("authorization")
    if not auth:
        return None, None

    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None, None

    token = parts[1]
    try:
        payload = decode_access_token(token)
    except Exception:
        return None, None

    user_id = payload.get("sub")
    session_id = payload.get("sid")
    if not user_id or not session_id:
        return None, None
    return str(user_id), str(session_id)


async def _write_log(payload: Dict[str, Any]) -> None:
    try:
        session_factory = get_session_factory()
    except Exception:
        return

    async with session_factory() as db:
        async with db.begin():
            db.add(ApiRequestLog(**payload))


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not request.url.path.startswith("/api/") or request.method.upper() == "OPTIONS":
            return await call_next(request)

        settings = get_settings()
        if not settings.DATABASE_URL:
            return await call_next(request)
        max_bytes = settings.REQUEST_LOG_MAX_BODY_BYTES

        started_at = datetime.now(timezone.utc)
        start_perf = time.perf_counter()

        request_headers = _sanitize_headers(dict(request.headers))
        query_params = dict(request.query_params)
        request_body_bytes = await request.body()
        request_body_json, request_body_text = _parse_body(
            request_body_bytes,
            request.headers.get("content-type", ""),
            max_bytes,
        )

        try:
            response = await call_next(request)
            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            response_body_bytes = b"".join(chunks)
        except Exception as exc:
            finished_at = datetime.now(timezone.utc)
            duration_ms = int((time.perf_counter() - start_perf) * 1000)

            user_id, session_id = await _resolve_auth_context(request)
            log_payload: Dict[str, Any] = {
                "user_id": user_id,
                "session_id": session_id,
                "method": request.method.upper(),
                "path": request.url.path,
                "query_params": query_params or None,
                "request_headers": request_headers or None,
                "request_body_json": request_body_json,
                "request_body_text": request_body_text,
                "response_status_code": 500,
                "response_headers": None,
                "response_body_json": None,
                "response_body_text": None,
                "error_message": str(exc),
                "client_ip": (request.client.host if request.client else None),
                "user_agent": request.headers.get("user-agent"),
                "started_at": started_at,
                "finished_at": finished_at,
                "duration_ms": duration_ms,
            }
            await _write_log(log_payload)
            raise

        finished_at = datetime.now(timezone.utc)
        duration_ms = int((time.perf_counter() - start_perf) * 1000)

        response_headers = _sanitize_headers(dict(response.headers))
        response_body_json, response_body_text = _parse_body(
            response_body_bytes,
            response.headers.get("content-type", ""),
            max_bytes,
        )

        user_id, session_id = await _resolve_auth_context(request)
        log_payload = {
            "user_id": user_id,
            "session_id": session_id,
            "method": request.method.upper(),
            "path": request.url.path,
            "query_params": query_params or None,
            "request_headers": request_headers or None,
            "request_body_json": request_body_json,
            "request_body_text": request_body_text,
            "response_status_code": response.status_code,
            "response_headers": response_headers or None,
            "response_body_json": response_body_json,
            "response_body_text": response_body_text,
            "error_message": None,
            "client_ip": (request.client.host if request.client else None),
            "user_agent": request.headers.get("user-agent"),
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_ms": duration_ms,
        }

        existing_background = response.background
        background = BackgroundTasks()

        if isinstance(existing_background, BackgroundTasks):
            for task in existing_background.tasks:
                background.tasks.append(task)
        elif isinstance(existing_background, BackgroundTask):
            background.tasks.append(existing_background)

        background.add_task(_write_log, log_payload)

        rebuilt = Response(
            content=response_body_bytes,
            status_code=response.status_code,
            media_type=response.media_type,
            background=background,
        )
        # Preserve duplicate headers such as multiple `set-cookie`.
        rebuilt.raw_headers = list(response.raw_headers)
        return rebuilt
