from typing import Any

from django.contrib.auth import get_user_model
from django.core.cache import cache
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
        cache.clear()

    def test_find_email_success(
        self,
    ) -> None:
        test_token = "verify_sms_token"
        cache.set(f"sms_token:{test_token}", "01012345678", timeout=600)

        data = {"name": "킹짱이준", "sms_token": test_token}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "t**r@e****e.com")
        self.assertIsNone(cache.get(f"sms_token:{test_token}"))

    def test_find_email_invalid_token(self) -> None:
        data = {"name": "킹짱이준", "sms_token": "dachung_fail_token"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sms_token", response.data["error_detail"])

    def test_find_email_user_not_found(self) -> None:
        test_token = "verify_sms_token"
        cache.set(f"sms_token:{test_token}", "01000001111", timeout=600)

        data = {"name": "지존소민", "sms_token": test_token}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data["error_detail"])
