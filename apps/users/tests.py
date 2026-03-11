from typing import Any, Dict

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class SignupTest(TestCase):
    user_data: Dict[str, Any]
    url: str
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        """클래스당 1번 실행"""
        cls.url = "/api/v1/accounts/signup"

        cls.user_data = {
            "email": "test@example.com",
            "nickname": "testuser",
            "password": "testpassword123",
            "name": "홍길동",
            "phone_number": "010-1234-5678",
            "birthday": "2000-09-25",
            "gender": "M",
            "email_token": "valid_email_token_123",
            "sms_token": "valid_sms_token_123",
        }

    def setUp(self) -> None:
        self.client = APIClient()

    def test_signup_success(self) -> None:
        """ 회원가입 성공 테스트(201) """
        data = self.user_data.copy()
        data["email"] = "success@example.com"
        data["nickname"] = "success"
        data["phone_number"] = "010-9999-0000"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=data["email"]).exists())

    def test_signup_missing_email_fail(self) -> None:
        """ 필수필드 누락 시 실패 (400) """

        data = self.user_data.copy()
        data.pop("email")

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_duplicate_fail(self) -> None:
        """ 닉네임,이메일,휴대폰 중복 시 (409) """

        User.objects.create(
            email="example@example.com",
            nickname="testuser",
            name="홍길동",
            phone_number="010-1111-2222",
            birthday="2000-09-25",
            gender="M",
            hashed_password="password123",
        )

        data = self.user_data.copy()
        data["email"] = "example@example.com"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
