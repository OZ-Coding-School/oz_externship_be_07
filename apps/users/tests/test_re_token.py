import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models.models import User


class TokenRefreshTest(TestCase):
    user: User
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email=f"u{uuid.uuid4().hex[:5]}@test.com",
            password="password123!",
            nickname=uuid.uuid4().hex[:10],
            name="순광팔",
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
