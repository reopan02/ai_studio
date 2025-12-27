from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import as_utc, utc_now
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.database import User, UserSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    user: User
    session: UserSession


async def get_auth_context(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    token = token or request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    session_id = payload.get("sid")
    if not user_id or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user: Optional[User] = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    session: Optional[UserSession] = await db.get(UserSession, session_id)
    now = utc_now()
    if session:
        try:
            expires_at = as_utc(session.expires_at)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired",
            )
    else:
        expires_at = None
    if (
        not session
        or session.user_id != user.id
        or session.revoked_at is not None
        or (expires_at is not None and expires_at <= now)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )

    return AuthContext(user=user, session=session)


async def get_current_user(context: AuthContext = Depends(get_auth_context)) -> User:
    return context.user


async def require_admin(context: AuthContext = Depends(get_auth_context)) -> User:
    if not context.user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return context.user
