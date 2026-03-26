from typing import Any

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class PasswordFindTest(APITestCase):
    user: Any
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="old_password123!",
            name="끝이보인다",
            phone_number="01012345678",
            birthday="1995-01-01",
        )
        cls.url = reverse("users:find-password")

    def setUp(self) -> None:
        cache.clear()

    def test_password_find_success(self) -> None:
        test_token = "valid_token_123"
        cache_key = f"email_token:{test_token}"
        cache.set(cache_key, self.user.email, timeout=600)

        data = {"email_token": test_token, "new_password": "new_password5678!"}

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "비밀번호 변경 성공.")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_password5678!"))

        self.assertIsNone(cache.get(cache_key))

    def test_password_find_fail_invalid_token(self) -> None:
        data = {"email_token": "wrong_token", "new_password": "new_password5678!"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email_token", response.data["error_detail"])
        self.assertEqual(response.data["error_detail"]["email_token"][0], "유효하지 않거나 만료된 토큰입니다.")

    def test_password_find_fail_missing_fields(self) -> None:
        data = {"email_token": "some_token"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
