from typing import Any
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class FindEmailViewTest(APITestCase):
    user: Any
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(
            email="testuser@example.com", name="킹짱이준", phone_number="01012345678", birthday="1995-01-01"
        )
        cls.url = reverse("users:find-email")

    def setUp(self) -> None:
        self.client = APIClient()

    @patch("apps.users.services.verify_sms_services.VerifySmsService.verify_code")
    def test_find_email_success(self, mock_verify: Any) -> None:
        mock_verify.return_value = True

        data = {"name": "킹짱이준", "phone_number": "01012345678", "code": "123456"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "t**r@e****e.com")

    @patch("apps.users.services.verify_sms_services.VerifySmsService.verify_code")
    def test_find_email_invalid_code(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = False

        data = {"name": "킹짱이준", "phone_number": "01012345678", "code": "000000"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data["error_detail"])

    @patch("apps.users.services.verify_sms_services.VerifySmsService.verify_code")
    def test_find_email_user_not_found(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = True

        data = {"name": "지존소민", "phone_number": "01000000000", "code": "123456"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data["error_detail"])
