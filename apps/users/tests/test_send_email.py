from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class EmailSendTest(APITestCase):
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

    # 요청한 이메일로 코드 발송 후 Redis 저장 확인
    def test_post_email_success(self) -> None:
        response = self.client.post(self.url, {"email": self.valid_email}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "이메일 인증 코드가 전송되었습니다.")

        self.assertIsNotNone(cache.get(f"verify:{self.valid_email}"))

    # 이메일 누락 검사
    def test_post_email_fail_field_missing(self) -> None:
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"]["email"][0], "이 필드는 필수 항목입니다.")

    # 이메일 형식 검사
    def test_post_email_fail_invalid_format(self) -> None:
        response = self.client.post(self.url, {"email": "invalid-email-format"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("올바른 이메일 형식이 아닙니다.", str(response.data["error_detail"]["email"][0]))

    # 이메일 도메인 검사
    def test_post_email_fail_non_existent_domain(self) -> None:
        fake_email = "test@hagisilta.com"
        response = self.client.post(self.url, {"email": fake_email}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("존재하지 않는 이메일 도메인", str(response.data["error_detail"]["email"][0]))
