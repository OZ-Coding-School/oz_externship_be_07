import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.choices import UserRole, UserStatus
from apps.users.models.models import User


class AdminUserSearchTest(APITestCase):
    admin_user: User
    normal_user: User
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_superuser(
            email="waterup@hyeono.com",
            password="password123!",
            name="물오른현오",
            nickname="보내고졌음",
            phone_number="01012345678",
            gender="M",
            birthday="2000-09-25",
        )

        cls.normal_user = User.objects.create_user(
            email="water@down.com",
            password="password123!",
            name="물오른고건님",
            nickname="난이겼는뎅",
            phone_number="01011112222",
            gender="M",
            birthday="1995-05-05",
        )

        User.objects.create_user(
            email="student@test.com",
            password="pwd",
            name="소민조교님",
            nickname="가위로이김",
            phone_number="01034345555",
            gender="F",
            birthday="2000-01-01",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVATED,
        )
        User.objects.create_user(
            email="withdrawn@test.com",
            password="pwd",
            name="이준코치님",
            nickname="나도가위로이김",
            phone_number="01023235555",
            gender="M",
            birthday="1990-01-01",
            role=UserRole.USER,
            status=UserStatus.WITHDREW,
        )

        cls.url = "/api/v1/admin/accounts"

    def test_admin_can_list_users(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)

    def test_filter_by_status(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"status": "WITHDREW"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["email"], "withdrawn@test.com")
        self.assertEqual(response.data["results"][0]["name"], "이준코치님")

    def test_search_by_name(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"search": "소민조교님"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nickname"], "가위로이김")

    def test_normal_user_cannot_access_admin_api(self) -> None:
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_get_user_detail(self) -> None:
        self.client.force_authenticate(user=self.admin_user)

        target_user = User.objects.get(email="withdrawn@test.com")

        detail_url = f"{self.url}/{target_user.id}"

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "이준코치님")

        self.assertIsInstance(response.data["assigned_courses"], list)
