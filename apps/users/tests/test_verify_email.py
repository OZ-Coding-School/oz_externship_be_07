from typing import Any

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class EmailVerifyTest(APITestCase):
    email: str
    code: str
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.email = "test@example.com"
        cls.code = "123456"

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("users:email-verify")

        cache.clear()
        cache.set(f"verify:{self.email}", self.code, timeout=300)

    def test_verify_email_success(self) -> None:
        data: dict[str, Any] = {"email": self.email, "code": self.code}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "이메일 인증에 성공하였습니다.")
        self.assertIn("email_token", response.data)
        self.assertEqual(len(response.data["email_token"]), 32)

        self.assertIsNone(cache.get(f"verify:{self.email}"))

    def test_verify_email_wrong_code(self) -> None:
        data: dict[str, Any] = {"email": self.email, "code": "999999"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("인증번호가 일치하지 않습니다.", str(response.data["error_detail"]["code"]))

    def test_verify_email_expired_code(self) -> None:
        data: dict[str, Any] = {"email": "no-requested@example.com", "code": self.code}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("인증 시간이 만료되었거나 잘못된 요청입니다.", str(response.data["error_detail"]["code"]))

    def test_verify_email_invalid_format(self) -> None:
        data: dict[str, Any] = {"email": self.email, "code": "abc123"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("인증번호는 숫자만 입력 가능합니다.", str(response.data["error_detail"]["code"]))

    def test_verify_email_brute_force_protection(self) -> None:
        data = {"email": self.email, "code": "999999"}

        for i in range(4):
            response = self.client.post(self.url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url, data, format="json")
        self.assertIn("인증 번호 5회 실패", str(response.data["error_detail"]["code"]))

        self.assertIsNone(cache.get(f"verify:{self.email}"))
        self.assertIsNone(cache.get(f"failure_count:{self.email}"))
