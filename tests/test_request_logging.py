import unittest


class TestRequestLoggingSanitization(unittest.TestCase):
    def test_sanitize_headers_drops_sensitive_headers(self) -> None:
        from app.middleware.request_logging import _sanitize_headers

        sanitized = _sanitize_headers(
            {
                "Authorization": "Bearer secret",
                "X-API-Key": "secret",
                "X-CSRF-Token": "csrf",
                "Content-Type": "application/json",
            }
        )

        self.assertNotIn("Authorization", sanitized)
        self.assertNotIn("X-API-Key", sanitized)
        self.assertIn("X-CSRF-Token", sanitized)
        self.assertIn("Content-Type", sanitized)


if __name__ == "__main__":
    unittest.main()
