from typing import Any

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class PhoneChangeAPITest(APITestCase):
    user: Any
    other_user: Any
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="giveup@gg.com",
            nickname="무너진현오",
            phone_number="01011112222",
            password="password123",
            birthday="2000-09-25",
            gender="M",
        )
        cls.other_user = User.objects.create_user(
            email="tekai@wall.com",
            nickname="버티는고건님",
            phone_number="01099998888",
            password="password123",
            birthday="2000-09-25",
            gender="M",
        )
        cls.url = reverse("users:change-phone")

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_phone_change_success(self) -> None:
        verify_token = "valid_token_123"
        new_number = "01055556666"
        cache.set(f"sms_token:{verify_token}", new_number, timeout=60)

        data = {"phone_verify_token": verify_token}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "휴대폰 번호 변경에 성공했습니다.")
        self.assertEqual(response.data["phone_number"], new_number)

        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, new_number)

    def test_phone_change_conflict(self) -> None:
        verify_token = "conflict_token"
        conflict_number = "01099998888"
        cache.set(f"sms_token:{verify_token}", conflict_number, timeout=60)

        data = {"phone_verify_token": verify_token}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error_detail"], "이미 등록된 휴대폰 번호입니다.")

    def test_phone_change_invalid_token(self) -> None:
        data = {"phone_verify_token": "invalid_token"}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_phone_change_unauthorized(self) -> None:
        self.client.force_authenticate(user=None)
        data = {"phone_verify_token": "token"}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
