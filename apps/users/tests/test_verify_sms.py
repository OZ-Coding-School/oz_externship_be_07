from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SmsVerifyTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("users:sms-verify")
        self.valid_phone = "010-1234-5678"
        self.invalid_code = "000000"
        cache.clear()

    @patch("apps.users.services.verify_sms_services.Client")
    def test_verify_sms_success(self, mock_twilio_client: MagicMock) -> None:
        mock_check = MagicMock()
        mock_check.status = "approved"

        mock_twilio_client.return_value.verify.v2.services.return_value.verification_checks.create.return_value = (
            mock_check
        )

        data = {"phone_number": "010-1234-5678", "code": "123456"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sms_token", response.data)

        sms_token = response.data["sms_token"]
        self.assertEqual(cache.get(f"sms_token:{sms_token}"), "01012345678")

    def test_verify_sms_fail_field(self) -> None:
        data = {"phone_number": "010-123", "code": "123456"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data["error_detail"])

    def test_verify_sms_no_code(self) -> None:
        data = {"phone_number": self.valid_phone}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
