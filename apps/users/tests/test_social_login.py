from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class SocialLoginTest(APITestCase):
    def setUp(self) -> None:
        self.kakao_callback_url = reverse("users:kakao-callback")
        self.naver_callback_url = reverse("users:naver-callback")

        self.user = User.objects.create(email="boss@test.com", nickname="생님", birthday="2000-01-01")

    @patch("apps.users.services.social_login_services.KakaoOAuthService.get_access_token")
    @patch("apps.users.services.social_login_services.KakaoOAuthService.get_user_info")
    @patch("apps.users.services.social_login_services.KakaoOAuthService.get_or_create_user")
    def test_kakao_login_success(
        self, mock_get_or_create_user: Any, mock_get_user_info: Any, mock_get_access_token: Any
    ) -> None:
        mock_get_or_create_user.return_value = self.user

        session = self.client.session
        session["social_login_state"] = "test_state"
        session.save()

        response: Any = self.client.get(self.kakao_callback_url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=true", response.url)
        self.assertIn("access_token", response.cookies)

    @patch("apps.users.services.social_login_services.KakaoOAuthService.get_access_token")
    def test_kakao_login_failure_invalid_code(self, mock_token: Any) -> None:
        mock_token.side_effect = Exception("Invalid Code")

        response: Any = self.client.get(self.kakao_callback_url, {"code": "wrong_code", "state": "any"})

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", response.url)

    @patch("apps.users.services.social_login_services.NaverOAuthService.get_access_token")
    @patch("apps.users.services.social_login_services.NaverOAuthService.get_user_info")
    @patch("apps.users.services.social_login_services.NaverOAuthService.get_or_create_user")
    def test_naver_login_success(self, mock_get_user: Any, mock_get_user_info: Any, mock_get_access_token: Any) -> None:
        mock_get_user.return_value = self.user

        session = self.client.session
        session["social_login_state"] = "test_state"
        session.save()

        response: Any = self.client.get(self.naver_callback_url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("provider=naver", response.url)
        self.assertIn("is_success=true", response.url)
        self.assertIn("access_token", response.cookies)

    @patch("apps.users.services.social_login_services.NaverOAuthService.get_access_token")
    def test_naver_login_failure_invalid_code(self, mock_token: Any) -> None:
        mock_token.side_effect = Exception("Naver Error")

        response: Any = self.client.get(self.naver_callback_url, {"code": "wrong_code", "state": "any"})

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("provider=naver", response.url)
        self.assertIn("is_success=false", response.url)
