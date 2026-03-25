import datetime
from typing import Any, cast

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.choices import UserStatus
from apps.users.models.models import Withdrawal

User = get_user_model()


class AccountRecoveryTest(APITestCase):
    user: Any
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="gwang@pal.com",
            password="password123!",
            name="순광팔",
            nickname="gwagpal",
            phone_number="010-1234-5678",
            gender="M",
            birthday=datetime.date(1990, 1, 1),
        )
        cls.url = reverse("users:restore")

    def setUp(self) -> None:
        cache.clear()

    def test_restore_account_success(self) -> None:
        user = self.user
        user.is_active = False
        user.status = UserStatus.DEACTIVATED
        user.save()

        Withdrawal.objects.create(
            user=user,
            reason="기타",
            reason_detail="테스트",
            due_date=timezone.now().date() + datetime.timedelta(days=30),
        )

        test_token = "test_token"
        cache_key = f"email_token:{test_token}"
        cache.set(cache_key, user.email, timeout=600)

        data: dict[str, str] = {"email_token": test_token}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "계정복구가 완료되었습니다.")

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(user.status, UserStatus.ACTIVATED)

        self.assertFalse(Withdrawal.objects.filter(user=user).exists())

        self.assertIsNone(cache.get(cache_key))

    def test_restore_account_fail_invalid_token(self) -> None:
        data = {"email_token": "email_token_123"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "유효하지 않거나 만료된 토큰입니다.")

    def test_restore_account_fail_missing_field(self) -> None:
        data: dict[str, Any] = {}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_detail = cast(dict[str, Any], response.data.get("error_detail"))
        self.assertIn("email_token", error_detail)
