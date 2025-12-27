from __future__ import annotations

from starlette.datastructures import Headers
from starlette.responses import FileResponse, Response
from starlette.staticfiles import NotModifiedResponse, StaticFiles
from starlette.types import Scope

from app.config import get_settings


class CacheControlStaticFiles(StaticFiles):
    def __init__(self, *args, cache_control: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._cache_control_override = cache_control

    def _resolve_cache_control(self) -> str | None:
        if self._cache_control_override is not None:
            return self._cache_control_override

        settings = get_settings()
        if settings.STATIC_CACHE_CONTROL:
            return settings.STATIC_CACHE_CONTROL

        if settings.ENV.lower() in {"prod", "production"}:
            return "public, max-age=31536000, immutable"

        return "no-store"

    def file_response(  # type: ignore[override]
        self,
        full_path,
        stat_result,
        scope: Scope,
        status_code: int = 200,
    ) -> Response:
        request_headers = Headers(scope=scope)
        response = FileResponse(full_path, status_code=status_code, stat_result=stat_result)
        cache_control = self._resolve_cache_control()
        if cache_control:
            response.headers["Cache-Control"] = cache_control
        if self.is_not_modified(response.headers, request_headers):
            return NotModifiedResponse(response.headers)
        return response

