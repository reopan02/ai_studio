import unittest


class TestRunningHubClientHelpers(unittest.TestCase):
    def test_build_image_to_video_realistic_payload_uses_expected_keys(self) -> None:
        from app.clients.runninghub_client import build_image_to_video_realistic_payload

        payload = build_image_to_video_realistic_payload(
            prompt="hello",
            resolution="720p",
            aspect_ratio="16:9",
            image_url="https://example.com/input.png",
            duration=4,
        )

        self.assertEqual(
            payload,
            {
                "prompt": "hello",
                "resolution": "720p",
                "aspectRatio": "16:9",
                "imageUrl": "https://example.com/input.png",
                "duration": "4",
            },
        )

    def test_extract_first_result_url_from_response(self) -> None:
        from app.clients.runninghub_client import extract_first_result_url

        url = extract_first_result_url(
            {
                "taskId": "t1",
                "status": "SUCCESS",
                "results": [{"url": "https://example.com/out.mp4", "outputType": "video"}],
            }
        )
        self.assertEqual(url, "https://example.com/out.mp4")

        self.assertIsNone(extract_first_result_url({"results": []}))
        self.assertIsNone(extract_first_result_url({"results": [{}]}))
        self.assertIsNone(extract_first_result_url({}))


if __name__ == "__main__":
    unittest.main()

