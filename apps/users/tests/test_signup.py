import uuid
from typing import Any, Dict

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models.models import User


class SignupTest(TestCase):
    user_data: Dict[str, Any]
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/accounts/signup"

    def setUp(self) -> None:
        self.client = APIClient()

        uid = uuid.uuid4().hex[:6]

        # 테스트별 고유 토큰으로 캐시 충돌 방지
        self.email_token = f"et_{uid}"
        self.sms_token = f"st_{uid}"

        cache.set(f"email_token:{self.email_token}", f"test_{uid}@example.com", timeout=3600)
        cache.set(f"sms_token:{self.sms_token}", f"010{uid}1234", timeout=3600)

        self.user_data = {
            "nickname": f"u{uid}",
            "password": "testpassword123",
            "name": "홍길동",
            "birthday": "2000-09-25",
            "gender": "M",
            "email_token": self.email_token,
            "sms_token": self.sms_token,
        }

    def test_signup_success(self) -> None:
        """회원가입 성공 테스트(201)"""
        data = self.user_data.copy()

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(nickname=data["nickname"]).exists())

        user = User.objects.get(nickname=data["nickname"])
        self.assertIn("@example.com", user.email)
        self.assertTrue(user.phone_number.startswith("010"))

        self.assertIsNone(cache.get(f"email_token:{self.email_token}"))
        self.assertIsNone(cache.get(f"sms_token:{self.sms_token}"))

    def test_signup_missing_field_fail(self) -> None:
        """필수필드 누락 시 실패 (400)"""
        data = self.user_data.copy()
        data.pop("name")

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_invalid_email_token_fail(self) -> None:
        """이메일 토큰 만료/무효 시 실패"""
        data = self.user_data.copy()
        data["email_token"] = "expired_token"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_invalid_sms_token_fail(self) -> None:
        """SMS 토큰 만료/무효 시 실패"""
        data = self.user_data.copy()
        data["sms_token"] = "expired_token"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_duplicate_nickname_fail(self) -> None:
        """닉네임 중복 시 (409)"""
        User.objects.create_user(
            email="existing@example.com",
            password="password123",
            nickname="dupuser",
            name="기존유저",
            phone_number="010-1111-2222",
            birthday="2000-09-25",
            gender="M",
        )

        data = self.user_data.copy()
        data["nickname"] = "dupuser"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
