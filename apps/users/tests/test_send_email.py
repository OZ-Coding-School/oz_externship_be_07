from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class SendEmailTest(APITestCase):
    url: str
    valid_email: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("users:email-send")
        cls.valid_email = "user@example.com"

    def setUp(self) -> None:
        self.client = APIClient()

    def tearDown(self) -> None:
        cache.clear()

    # 인증코드 발급 성공
    def test_send_email_success(self) -> None:
        response = self.client.post(self.url, {"email": self.valid_email}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "이메일 인증 코드가 전송되었습니다.")
        self.assertIsNotNone(cache.get(f"verify:{self.valid_email}"))

    # 인증코드 발급 실패 (이메일누락)
    def test_send_email_fail_field_missing(self) -> None:
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"]["email"][0], "이 필드는 필수 항목입니다.")

    # 인증코드 발급 실패2(형식 에러)
    def test_send_email_fail_invalid_format(self) -> None:
        response = self.client.post(self.url, {"email": "invalid-email-format"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("올바른 이메일 형식이 아닙니다.", str(response.data["error_detail"]["email"][0]))
