import asyncio
import base64
import os
import time
import unittest
from pathlib import Path

import httpx
import jwt


_ONE_BY_ONE_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/w8AAgMBg1G9GQAAAABJRU5ErkJggg=="
)


class TestRunningHubImageUpload(unittest.TestCase):
    def test_upload_runninghub_image_returns_public_url(self) -> None:
        os.environ["SUPABASE_JWT_SECRET"] = "test-secret"
        os.environ["DATABASE_URL"] = ""

        from app.config import get_settings

        get_settings.cache_clear()

        from app.main import app

        token = jwt.encode(
            {
                "sub": "11111111-1111-1111-1111-111111111111",
                "aud": "authenticated",
                "role": "authenticated",
                "exp": int(time.time()) + 3600,
            },
            "test-secret",
            algorithm="HS256",
        )

        png_bytes = base64.b64decode(_ONE_BY_ONE_PNG_BASE64)

        async def run() -> None:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                res = await client.post(
                    "/api/v1/uploads/runninghub/image",
                    headers={"Authorization": f"Bearer {token}"},
                    files={"image": ("tiny.png", png_bytes, "image/png")},
                )

                self.assertEqual(res.status_code, 200, res.text)
                payload = res.json()

                image_url = str(payload.get("image_url") or "")
                relative_url = str(payload.get("relative_url") or "")

                self.assertTrue(image_url.startswith("http://testserver/uploads/runninghub/"), image_url)
                self.assertTrue(relative_url.startswith("/uploads/runninghub/"), relative_url)

                saved_path = Path("app/static") / relative_url.lstrip("/")
                self.assertTrue(saved_path.exists(), str(saved_path))

                # Cleanup so the test is idempotent.
                saved_path.unlink(missing_ok=True)
                try:
                    saved_path.parent.rmdir()
                except OSError:
                    pass

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()

