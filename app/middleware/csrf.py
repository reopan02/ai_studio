from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        cookie_name: str = "csrf_token",
        header_name: str = "x-csrf-token",
        token_cookie_name: str = "access_token",
        protected_prefix: str = "/api/",
        exempt_paths: set[str] | None = None,
    ):
        super().__init__(app)
        self._cookie_name = cookie_name
        self._header_name = header_name
        self._token_cookie_name = token_cookie_name
        self._protected_prefix = protected_prefix
        self._exempt_paths = exempt_paths or {"/api/v1/auth/login", "/api/v1/auth/register"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return await call_next(request)

        path = request.url.path
        if not path.startswith(self._protected_prefix) or path in self._exempt_paths:
            return await call_next(request)

        if request.headers.get("authorization"):
            return await call_next(request)

        if not request.cookies.get(self._token_cookie_name):
            return await call_next(request)

        csrf_cookie = request.cookies.get(self._cookie_name)
        csrf_header = request.headers.get(self._header_name)
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return JSONResponse({"detail": "CSRF token missing or invalid"}, status_code=403)

        return await call_next(request)

