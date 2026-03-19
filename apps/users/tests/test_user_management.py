from typing import Any, cast

from django.contrib.auth.models import AbstractBaseUser
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.choices import UserRole, UserStatus
from apps.users.models.models import User


class AdminUserDeleteTest(TestCase):
    admin_user: User
    regular_user: User
    target_user: User
    client: APIClient
    base_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.base_url = "/api/v1/admin/accounts/"
        user_manager: Any = User.objects

        # 관리자 생성
        cls.admin_user = user_manager.create(
            email="admin@example.com",
            nickname="집이지만",
            name="admin",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVATED,
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.admin_user.is_staff = True
        cls.admin_user.save()

        # 일반 유저 생성
        cls.target_user = user_manager.create(
            email="user@example.com",
            nickname="집가고싶다",
            name="user",
            role=UserRole.USER,
            status=UserStatus.ACTIVATED,
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        # 삭제 대상 유저 생성
        cls.target_user = user_manager.create(
            email="target@example.com",
            nickname="target_test",
            role=UserRole.USER,
            status=UserStatus.ACTIVATED,
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_delete_user_success_200(self) -> None:
        """200 OK: 어드민이 유저를 성공적으로 삭제하는 경우"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))
        url = f"{self.base_url}{self.target_user.id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["detail"],
            f"유저 데이터가 삭제되었습니다. - pk: {self.target_user.id}"
        )
        # DB에서 실제로 삭제되었는지 확인
        self.assertFalse(User.objects.filter(id=self.target_user.id).exists())

    def test_delete_user_fail_401_unauthorized(self) -> None:
        """401 Unauthorized: 인증 데이터가 없는 경우"""
        url = f"{self.base_url}{self.target_user.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_delete_user_fail_403_forbidden(self) -> None:
        """403 Forbidden: 관리자 권한이 없는 유저가 삭제를 시도하는 경우"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.regular_user))
        url = f"{self.base_url}{self.target_user.id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], "권한이 없습니다.")

    def test_delete_user_fail_404_not_found(self) -> None:
        """404 Not Found: 존재하지 않는 유저 ID를 삭제하려는 경우"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))
        invalid_url = f"{self.base_url}9999/" # 존재하지 않는 ID

        response = self.client.delete(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "사용자 정보를 찾을 수 없습니다.")