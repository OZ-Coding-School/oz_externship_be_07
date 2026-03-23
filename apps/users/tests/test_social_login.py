from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.choices import SocialProvider
from apps.users.models import SocialUser

User = get_user_model()


class SocialLoginTest(APITestCase):
    def setUp(self) -> None:
        self.kakao_callback_url = reverse("users:kakao-callback")
        self.naver_callback_url = reverse("users:naver-callback")

    @patch("apps.users.services.social_login_services.requests.get")
    @patch("apps.users.services.social_login_services.requests.post")
    def test_kakao_login_success(self, mock_post: Any, mock_get: Any) -> None:
        session = self.client.session
        session["social_login_state"] = "test_state"
        session.save()

        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {"access_token": "fake_kakao_token"}

        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {"id": 123456789, "kakao_account": {"email": "test@kakao.com"}}

        response = self.client.get(self.kakao_callback_url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

        self.assertTrue(SocialUser.objects.filter(provider=SocialProvider.KAKAO, provider_id="123456789").exists())

    @patch("apps.users.services.social_login_services.requests.post")
    def test_kakao_login_failure_invalid_code(self, mock_post: Any) -> None:
        mock_post.return_value.ok = False

        response = self.client.get(self.kakao_callback_url, {"code": "wrong_code"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("apps.users.services.social_login_services.requests.get")
    @patch("apps.users.services.social_login_services.requests.post")
    def test_naver_login_success(self, mock_post: Any, mock_get: Any) -> None:
        session = self.client.session
        session["social_login_state"] = "test_state"
        session.save()

        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {"access_token": "fake_naver_token"}

        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            "response": {"id": "naver_12345", "email": "test@naver.com", "name": "팀장님"}
        }

        response = self.client.get(self.naver_callback_url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

        self.assertTrue(SocialUser.objects.filter(provider=SocialProvider.NAVER, provider_id="naver_12345").exists())

    @patch("apps.users.services.social_login_services.requests.post")
    def test_naver_login_failure_invalid_code(self, mock_post: Any) -> None:
        mock_post.return_value.ok = False

        response = self.client.get(self.naver_callback_url, {"code": "wrong_code"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
