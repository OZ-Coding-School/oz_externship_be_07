import uuid
from datetime import date, timedelta
from typing import Any, Dict
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.choices import WithdrawalReason
from apps.users.models.models import User, Withdrawal


class SignupTest(TestCase):
    user_data: Dict[str, Any]
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("users:signup")

    def setUp(self) -> None:
        self.client = APIClient()

        uid = uuid.uuid4().hex[:6]

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
        data = self.user_data.copy()
        data.pop("name")

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_invalid_email_token_fail(self) -> None:
        data = self.user_data.copy()
        data["email_token"] = "expired_token"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_invalid_sms_token_fail(self) -> None:
        data = self.user_data.copy()
        data["sms_token"] = "expired_token"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.users.services.auth_services.cache")
    def test_signup_duplicate_nickname_fail(self, mock_cache: Any) -> None:
        mock_cache.get.side_effect = lambda key: {
            "email_token:dup_et": "dup@example.com",
            "sms_token:dup_st": "01099998888",
        }.get(key)

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
        data["email_token"] = "dup_et"
        data["sms_token"] = "dup_st"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


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

        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("탈퇴 신청한 계정입니다", str(response.data))  # type: ignore
        self.assertEqual(response.data["expire_at"], due_date.strftime("%Y-%m-%d"))  # type: ignore

    def test_login_non_existent_user_fail(self) -> None:
        data = {"email": "none@example.com", "password": self.password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTest(TestCase):
    user: User
    url: str
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email=f"logout_{uuid.uuid4().hex[:5]}@test.com",
            password="password123!",
            nickname=f"nick_{uuid.uuid4().hex[:5]}",
            name="홍길동",
            birthday="1995-01-01",
            gender="M",
        )
        cls.url = reverse("users:logout")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_logout_success(self) -> None:
        self.client.force_authenticate(user=self.user)

        self.client.cookies["refresh_token"] = "imnottoken"

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_cookie = response.cookies.get("refresh_token")
        self.assertEqual(refresh_cookie.value, "")  # type: ignore
        self.assertEqual(refresh_cookie["max-age"], 0)  # type: ignore

    def test_logout_without_login(self) -> None:
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTest(TestCase):
    user: User
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email=f"u{uuid.uuid4().hex[:5]}@test.com",
            password="passwood123!",
            nickname=uuid.uuid4().hex[:10],
            name="순광팔",
            phone_number=f"010{uuid.uuid4().hex[:8]}",
            birthday="2000-09-25",
            gender="M",
        )
        cls.url = reverse("users:token-refresh")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_token_refresh_success(self) -> None:
        refresh = RefreshToken.for_user(self.user)

        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)  # type: ignore
        self.assertNotIn("refresh_token", response.data)  # type: ignore

    def test_token_refresh_fail_no_cookie(self) -> None:
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh_token", response.data["error_detail"])  # type: ignore
        self.assertEqual(response.data["error_detail"]["refresh_token"][0], "이 필드는 필수 항목입니다.")  # type: ignore

    def test_token_refresh_fail_invalid_token(self) -> None:
        self.client.cookies["refresh_token"] = "wrong-token-value"

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"]["detail"], "로그인 세션이 만료되었습니다.")  # type: ignore
