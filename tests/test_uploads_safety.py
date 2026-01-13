import unittest


class TestUploadsSafety(unittest.TestCase):
    def test_is_own_product_image_url(self) -> None:
        from app.api.v1.uploads import _is_own_product_image_url

        user_id = "11111111-1111-1111-1111-111111111111"

        self.assertTrue(_is_own_product_image_url(f"/uploads/products/{user_id}/p1.jpg", user_id))
        self.assertTrue(_is_own_product_image_url(f"/static/uploads/products/{user_id}/p1.jpg", user_id))

        self.assertFalse(_is_own_product_image_url("/uploads/products/other/p1.jpg", user_id))
        self.assertFalse(_is_own_product_image_url("/static/uploads/products/other/p1.jpg", user_id))
        self.assertFalse(_is_own_product_image_url("/uploads/other/p1.jpg", user_id))


if __name__ == "__main__":
    unittest.main()

