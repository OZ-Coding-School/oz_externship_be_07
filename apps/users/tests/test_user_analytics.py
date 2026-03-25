from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.users.models.models import User


class TestAdminSignupTrend(APITestCase):
    admin: User
    url: str
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin = User.objects.create_superuser(
            email="admin@example.com",
            name="어드민",
            nickname="통과돼주세요",
            phone_number="01000000000",
            birthday="19900101",
            is_staff=True,
        )
        cls.url = reverse("admin-signup-trend")

        now = timezone.now()
        last_month = now - timedelta(days=32)

        for i in range(3):
            User.objects.create_user(
                email=f"recent_{i}@example.com",
                name=f"최근_{i}",
                nickname=f"recent_{i}",
                phone_number=f"0101111000{i}",
                birthday="19950505",
            )
        User.objects.filter(email__contains="recent").update(created_at=now)

        for i in range(2):
            User.objects.create_user(
                email=f"old_{i}@example.com",
                name=f"과거_{i}",
                nickname=f"old_{i}",
                phone_number=f"0102222000{i}",
                birthday="19921212",
            )
        User.objects.filter(email__contains="old").update(created_at=last_month)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_signup_trend_monthly_success(self) -> None:
        response = self.client.get(self.url, {"interval": "monthly"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 6)

        items = response.data.get("items", [])
        self.assertTrue(len(items) > 0)
        self.assertEqual(items[-1]["count"], 4)

    def test_signup_trend_forbidden_for_normal_user(self) -> None:
        normal_user = User.objects.create_user(
            email="normal@example.com",
            name="일반유저",
            nickname="이젠통과해주세요",
            phone_number="01099999999",
            birthday="20000101",
        )
        self.client.force_authenticate(user=normal_user)

        response = self.client.get(self.url, {"interval": "monthly"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
