from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthContext, get_auth_context
from app.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.database import User, UserLoginLog, UserSession
from app.models.schemas import TokenResponse, UserLoginRequest, UserPublic, UserRegisterRequest

router = APIRouter()


@router.post("/auth/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    stmt = select(User).where(or_(User.username == payload.username, User.email == payload.email))
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already registered")

    user = User(
        username=payload.username,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        is_admin=payload.username.lower() == "admin",
        storage_quota_bytes=settings.DEFAULT_STORAGE_QUOTA_BYTES,
        storage_used_bytes=0,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenResponse)
async def login_user(
    payload: UserLoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    set_cookie: bool = Query(default=False),
):
    stmt = select(User).where(or_(User.username == payload.username_or_email, User.email == payload.username_or_email))
    user = (await db.execute(stmt)).scalar_one_or_none()

    ip_address = (request.client.host if request.client else None)
    user_agent = request.headers.get("user-agent")

    if not user:
        db.add(
            UserLoginLog(
                user_id=None,
                username_or_email=payload.username_or_email,
                success=False,
                failure_reason="user_not_found",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    if not user.is_active:
        db.add(
            UserLoginLog(
                user_id=user.id,
                username_or_email=payload.username_or_email,
                success=False,
                failure_reason="inactive_user",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    if not verify_password(payload.password, user.password_hash):
        db.add(
            UserLoginLog(
                user_id=user.id,
                username_or_email=payload.username_or_email,
                success=False,
                failure_reason="invalid_password",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    settings = get_settings()
    now = datetime.now(timezone.utc)
    session = UserSession(
        user_id=user.id,
        expires_at=now + timedelta(days=settings.JWT_SESSION_EXPIRE_DAYS),
        ip_address=ip_address,
        user_agent=user_agent,
    )

    user.last_login_at = now
    db.add(session)
    db.add(
        UserLoginLog(
            user_id=user.id,
            username_or_email=payload.username_or_email,
            success=True,
            failure_reason=None,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )
    await db.flush()
    access_token = create_access_token(subject=user.id, session_id=session.id)
    await db.commit()

    if set_cookie:
        csrf_token = secrets.token_urlsafe(32)
        max_age = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=max_age,
            path="/",
        )
        response.set_cookie(
            "csrf_token",
            csrf_token,
            httponly=False,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=max_age,
            path="/",
        )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        session_id=session.id,
    )


@router.get("/auth/me", response_model=UserPublic)
async def get_me(context: AuthContext = Depends(get_auth_context)):
    return context.user


@router.post("/auth/logout")
async def logout(
    response: Response,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    session = await db.get(UserSession, context.session.id)
    if session and session.revoked_at is None:
        session.revoked_at = now
        await db.commit()
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("csrf_token", path="/")
    return {"message": "Logged out"}
