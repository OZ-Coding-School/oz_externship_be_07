from typing import Any
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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

    @patch("apps.users.services.find_email_services.Client")
    def test_find_email_success(self, mock_client_cls: MagicMock) -> None:
        mock_check = MagicMock()
        mock_check.status = "approved"
        mock_client_cls.return_value.verify.v2.services.return_value.verification_checks.create.return_value = (
            mock_check
        )

        data = {"name": "킹짱이준", "phone_number": "01012345678", "code": "123456"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "t**r@e****e.com")

    @patch("apps.users.services.find_email_services.Client")
    def test_find_email_invalid_code(self, mock_client_cls: MagicMock) -> None:
        mock_check = MagicMock()
        mock_check.status = "pending"
        mock_client_cls.return_value.verify.v2.services.return_value.verification_checks.create.return_value = (
            mock_check
        )

        data = {"name": "킹짱이준", "phone_number": "01012345678", "code": "000000"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data["error_detail"])

    @patch("apps.users.services.find_email_services.Client")
    def test_find_email_user_not_found(self, mock_client_cls: MagicMock) -> None:
        mock_check = MagicMock()
        mock_check.status = "approved"
        mock_client_cls.return_value.verify.v2.services.return_value.verification_checks.create.return_value = (
            mock_check
        )

        data = {"name": "지존소민", "phone_number": "01000001111", "code": "123456"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data["error_detail"])
