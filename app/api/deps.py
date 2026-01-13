from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request, status

from app.config import get_settings
from app.core.supabase_auth import verify_supabase_jwt


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    claims: dict[str, Any]


def authenticate_supabase_bearer(authorization: str | None, *, jwt_secret: str) -> AuthContext:
    """
    Authenticate using `Authorization: Bearer <supabase_access_token>`.

    This function is intentionally pure-ish (no FastAPI objects) to keep it testable.
    """
    if not authorization:
        raise ValueError("Not authenticated")

    parts = str(authorization).strip().split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValueError("Invalid authorization scheme")

    token = parts[1].strip()
    claims = verify_supabase_jwt(token, jwt_secret=jwt_secret)
    return AuthContext(user_id=str(claims["sub"]), claims=claims)


async def get_auth_context(
    request: Request,
) -> AuthContext:
    settings = get_settings()
    if not settings.SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET is not configured",
        )

    try:
        return authenticate_supabase_bearer(
            request.headers.get("authorization"),
            jwt_secret=settings.SUPABASE_JWT_SECRET,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc) or "Not authenticated",
        ) from exc


async def get_current_user(context: AuthContext = Depends(get_auth_context)) -> AuthContext:
    return context
