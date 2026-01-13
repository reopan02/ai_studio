from __future__ import annotations

from typing import Any

import jwt


def verify_supabase_jwt(
    token: str,
    *,
    jwt_secret: str,
    expected_aud: str | None = "authenticated",
) -> dict[str, Any]:
    """
    Verify a Supabase access token (self-hosted: HS256).

    Returns the decoded claims dict.
    Raises ValueError on any verification or validation failure.
    """
    if not jwt_secret:
        raise ValueError("SUPABASE_JWT_SECRET is required")

    raw = str(token or "").strip()
    if not raw:
        raise ValueError("Missing bearer token")

    try:
        claims = jwt.decode(
            raw,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except Exception as exc:
        raise ValueError("Invalid Supabase token") from exc

    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub.strip():
        raise ValueError("Supabase token missing 'sub'")

    if expected_aud is not None:
        aud = claims.get("aud")
        if isinstance(aud, str):
            aud_ok = aud == expected_aud
        elif isinstance(aud, list):
            aud_ok = expected_aud in aud
        else:
            aud_ok = False
        if not aud_ok:
            raise ValueError("Supabase token has unexpected 'aud'")

    return claims

