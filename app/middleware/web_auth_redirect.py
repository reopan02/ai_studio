from __future__ import annotations

from urllib.parse import quote

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from app.core.cache import TTLCache
from app.core.datetime_utils import as_utc, utc_now
from app.core.security import decode_access_token
from app.db.session import get_session_factory
from app.models.database import User, UserSession


_session_cache: TTLCache[str, str] = TTLCache(ttl_seconds=30, max_items=50_000)


class WebAuthRedirectMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, login_path: str = "/login"):
        super().__init__(app)
        self._login_path = login_path

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        if path.startswith("/api/") or path in {self._login_path, "/health", "/favicon.ico"}:
            return await call_next(request)

        if path.startswith("/static/") or path.startswith("/images_editing/"):
            if path.endswith(".html") and path not in {"/static/login.html", "/images_editing/index.html"}:
                return self._redirect_to_login(request)
            return await call_next(request)

        token = request.cookies.get("access_token")
        if not token:
            return self._redirect_to_login(request)

        try:
            payload = decode_access_token(token)
        except Exception:
            return self._redirect_to_login(request)

        user_id = payload.get("sub")
        session_id = payload.get("sid")
        if not user_id or not session_id:
            return self._redirect_to_login(request)

        cached_user_id = _session_cache.get(str(session_id))
        if cached_user_id and cached_user_id == str(user_id):
            return await call_next(request)

        try:
            session_factory = get_session_factory()
        except Exception:
            return await call_next(request)

        async with session_factory() as db:
            user = await db.get(User, user_id)
            if not user or not user.is_active:
                return self._redirect_to_login(request)

            session = await db.get(UserSession, session_id)
            now = utc_now()
            try:
                expires_at = as_utc(session.expires_at) if session else None
            except Exception:
                return self._redirect_to_login(request)
            if (
                not session
                or session.user_id != user.id
                or session.revoked_at is not None
                or (expires_at is not None and expires_at <= now)
            ):
                return self._redirect_to_login(request)

        _session_cache.set(str(session_id), str(user_id))
        return await call_next(request)

    def _redirect_to_login(self, request: Request) -> Response:
        next_path = request.url.path
        if request.url.query:
            next_path = f"{next_path}?{request.url.query}"
        return RedirectResponse(f"{self._login_path}?next={quote(next_path)}", status_code=303)
