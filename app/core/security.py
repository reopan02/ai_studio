from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from passlib.context import CryptContext

from app.config import get_settings

_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


def create_access_token(*, subject: str, session_id: str) -> str:
    settings = get_settings()
    if not settings.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is required for authentication")

    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": subject,
        "sid": session_id,
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is required for authentication")

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "sub", "sid"]},
    )
