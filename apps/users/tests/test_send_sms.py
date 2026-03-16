from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class SendSmsTest(APITestCase):
    url: str
    valid_phone: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("users:sms-send")
        cls.valid_phone = "010-1234-5678"

    def setUp(self) -> None:
        self.client = APIClient()
        cache.clear()

    # SMS 인증코드 발급 성공
    @patch("apps.users.services.send_sms_services.Client")
    def test_send_sms_success(self, mock_send_sms: MagicMock) -> None:
        response = self.client.post(self.url, {"phone_number": self.valid_phone}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "인증 코드가 전송 되었습니다.")
        self.assertTrue(mock_send_sms.called)

        phone_number = self.valid_phone.replace("-", "")
        self.assertIsNotNone(cache.get(f"verify_sms:{phone_number}"))

    # SMS 인증코드 발급 실패 (휴대폰 번호 누락)
    def test_send_sms_fail_field_missing(self) -> None:
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"]["phone_number"][0], "이 필드는 필수 항목입니다.")

    # SMS 인증코드 발급 실패2 (형식 에러)
    def test_send_sms_fail_invalid_format(self) -> None:
        response = self.client.post(self.url, {"phone_number": "010-abc-1234"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("올바른 휴대폰 번호 형식이 아닙니다.", str(response.data["error_detail"]["phone_number"][0]))
