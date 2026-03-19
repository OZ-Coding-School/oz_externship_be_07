import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models.models import User


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
