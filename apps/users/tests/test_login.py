import uuid
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.choices import WithdrawalReason
from apps.users.models.models import User, Withdrawal


class LoginTest(TestCase):
    email: str
    password: str
    user: User
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.email = f"u{uuid.uuid4().hex[:5]}@a.com"
        cls.password = "password123!"
        cls.user = User.objects.create_user(
            email=cls.email,
            password=cls.password,
            nickname=uuid.uuid4().hex[:10],
            name="홍길동",
            phone_number=f"010{uuid.uuid4().hex[:8]}",
            birthday="1995-01-01",
            gender="M",
        )
        cls.url = reverse("users:login")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_success_and_cookie_check(self) -> None:
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access_token", response.data)  # type: ignore

        self.assertNotIn("refresh", response.data)  # type: ignore
        self.assertIn("refresh_token", response.cookies)

    def test_login_invalid_password_fail(self) -> None:
        data = {"email": self.email, "password": "wrong_password"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "이메일 또는 비밀번호가 잘못되었습니다.")  # type: ignore

    def test_login_withdrawn_user_403_fail(self) -> None:
        due_date = date.today() + timedelta(days=30)
        Withdrawal.objects.create(
            user=self.user, reason=WithdrawalReason.OTHER, reason_detail="테스트 탈퇴", due_date=due_date
        )

        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("탈퇴 신청한 계정입니다", str(response.data))  # type: ignore
        self.assertEqual(response.data["expire_at"], due_date.strftime("%Y-%m-%d"))  # type: ignore

    def test_login_non_existent_user_fail(self) -> None:
        data = {"email": "none@example.com", "password": self.password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
