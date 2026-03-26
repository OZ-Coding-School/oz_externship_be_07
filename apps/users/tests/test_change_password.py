import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class PasswordChangeTest(APITestCase):
    user: Any
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="oldPassword123!",
            name="테스터",
            nickname="tester",
            phone_number="010-1111-2222",
            gender="M",
            birthday=datetime.date(1995, 5, 5),
        )
        cls.url = reverse("users:change-password")

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_password_change_success(self) -> None:
        data = {"old_password": "oldPassword123!", "new_password": "newPassword456@"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "비밀번호 변경 성공.")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newPassword456@"))

    def test_password_change_fail_wrong_old_password(self) -> None:
        data = {"old_password": "wrongPassword!", "new_password": "newPassword456@"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data["error_detail"])

    def test_password_change_fail_same_password(self) -> None:
        data = {"old_password": "oldPassword123!", "new_password": "oldPassword123!"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data["error_detail"])

    def test_password_change_fail_unauthorized(self) -> None:
        self.client.force_authenticate(user=None)
        data = {"old_password": "...", "new_password": "..."}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
