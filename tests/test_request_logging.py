import unittest


class TestRequestLoggingSanitization(unittest.TestCase):
    def test_sanitize_headers_drops_runninghub_token(self) -> None:
        from app.middleware.request_logging import _sanitize_headers

        sanitized = _sanitize_headers(
            {
                "X-RunningHub-Token": "secret",
                "X-CSRF-Token": "csrf",
                "Content-Type": "application/json",
            }
        )

        self.assertNotIn("X-RunningHub-Token", sanitized)
        self.assertIn("X-CSRF-Token", sanitized)
        self.assertIn("Content-Type", sanitized)


if __name__ == "__main__":
    unittest.main()

