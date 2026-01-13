import time
import unittest

import jwt


class TestSupabaseJwtVerification(unittest.TestCase):
    def test_verify_supabase_jwt_accepts_valid_token(self) -> None:
        from app.core.supabase_auth import verify_supabase_jwt

        secret = "test-secret"
        token = jwt.encode(
            {
                "sub": "00000000-0000-0000-0000-000000000000",
                "aud": "authenticated",
                "role": "authenticated",
                "exp": int(time.time()) + 3600,
            },
            secret,
            algorithm="HS256",
        )

        claims = verify_supabase_jwt(token, jwt_secret=secret)
        self.assertEqual(claims["sub"], "00000000-0000-0000-0000-000000000000")

    def test_verify_supabase_jwt_rejects_invalid_signature(self) -> None:
        from app.core.supabase_auth import verify_supabase_jwt

        token = jwt.encode(
            {
                "sub": "00000000-0000-0000-0000-000000000000",
                "aud": "authenticated",
                "role": "authenticated",
                "exp": int(time.time()) + 3600,
            },
            "right-secret",
            algorithm="HS256",
        )

        with self.assertRaises(ValueError):
            verify_supabase_jwt(token, jwt_secret="wrong-secret")

    def test_verify_supabase_jwt_requires_sub(self) -> None:
        from app.core.supabase_auth import verify_supabase_jwt

        secret = "test-secret"
        token = jwt.encode(
            {
                "aud": "authenticated",
                "role": "authenticated",
                "exp": int(time.time()) + 3600,
            },
            secret,
            algorithm="HS256",
        )

        with self.assertRaises(ValueError):
            verify_supabase_jwt(token, jwt_secret=secret)


if __name__ == "__main__":
    unittest.main()

