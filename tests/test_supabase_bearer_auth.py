import time
import unittest

import jwt


class TestSupabaseBearerAuth(unittest.TestCase):
    def test_authenticate_supabase_bearer_accepts_bearer_header(self) -> None:
        from app.api.deps import authenticate_supabase_bearer

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

        ctx = authenticate_supabase_bearer(f"Bearer {token}", jwt_secret=secret)
        self.assertEqual(ctx.user_id, "00000000-0000-0000-0000-000000000000")

    def test_authenticate_supabase_bearer_rejects_missing_header(self) -> None:
        from app.api.deps import authenticate_supabase_bearer

        with self.assertRaises(ValueError):
            authenticate_supabase_bearer(None, jwt_secret="secret")


if __name__ == "__main__":
    unittest.main()

