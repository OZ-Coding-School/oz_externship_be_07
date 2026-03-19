import uuid
from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.choices import SocialProvider
from apps.users.models import SocialUser

User = get_user_model()


class SocialLoginTest(APITestCase):
    def setUp(self):
        self.kakao_url = reverse("users:kakao-login")
        self.naver_url = reverse("users:naver-login")

    @patch("apps.users.services.social_login_services.requests.post")
    @patch("apps.users.services.social_login_services.requests.get")
    def test_kakao_login_success(self, mock_get, mock_post):

        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {"access_token": "fake_kakao_token"}

        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {"id": 123456789, "properties": {"nickname": "카카오톡유저"}}

        response = self.client.get(self.kakao_url, {"code": "test_code"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertTrue(response.data["is_created"])

        self.assertTrue(User.objects.filter(email="kakao_123456789@kakao.com").exists())
        self.assertTrue(SocialUser.objects.filter(provider=SocialProvider.KAKAO).exists())

    @patch("apps.users.services.social_login_services.requests.post")
    def test_login_failure_invalid_code(self, mock_post):
        mock_post.return_value.ok = False

        response = self.client.get(self.kakao_url, {"code": "wrong_code"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
