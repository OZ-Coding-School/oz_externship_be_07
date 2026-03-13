from typing import Any, Dict

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models.models import User


class SignupTest(TestCase):
    user_data: Dict[str, Any]
    url: str
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        """클래스당 1번 실행"""
        cls.url = "/api/v1/accounts/signup"

        cls.user_data = {
            "nickname": "testuser",
            "password": "testpassword123",
            "name": "홍길동",
            "birthday": "2000-09-25",
            "gender": "M",
            "email_token": "valid_email_token_123",
            "sms_token": "valid_sms_token_123",
        }

    def setUp(self) -> None:
        self.client = APIClient()
        cache.clear()
        cache.set("email_token:valid_email_token_123", "test@example.com", timeout=3600)
        cache.set("sms_token:valid_sms_token_123", "010-1234-5678", timeout=3600)

    def test_signup_success(self) -> None:
        """회원가입 성공 테스트(201)"""
        data = self.user_data.copy()

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(name=data["name"]).exists())

        user = User.objects.get(name=data["name"])
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.phone_number, "010-1234-5678")

        self.assertIsNone(cache.get("email_token:valid_email_token_123"))
        self.assertIsNone(cache.get("sms_token:valid_sms_token_123"))

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
            nickname="testuser",
            name="기존유저",
            phone_number="010-1111-2222",
            birthday="2000-09-25",
            gender="M",
        )

        data = self.user_data.copy()

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
