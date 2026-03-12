from typing import Any, Dict, cast

from django.contrib.auth.models import AbstractBaseUser
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models.models import User


class AdminUserSearchTest(TestCase):
    admin_user: User
    target_user: User
    client: APIClient
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/admin/students/"
        user_manager: Any = User.objects

        # 관리자 생성
        cls.admin_user = user_manager.create(
            email="admin@example.com",
            name="관리자",
            role="ADMIN",
            birthday="1990-01-01",
            phone_number="01000000000",
            status="ACTIVATED",
        )
        setattr(cls.admin_user, "is_staff", True)

        cls.target_user = user_manager.create(
            email="user@example.com",
            nickname="testuser",
            name="홍길동",
            phone_number="01012345678",
            birthday="1998-08-29",
            status="ACTIVATED",
            role="STUDENT",
        )
        setattr(cls.target_user, "is_staff", False)

    def setUp(self) -> None:
        self.client = APIClient()
        # 기본적으로 관리자로 로그인 상태 유지
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def test_get_student_list_success(self) -> None:
        # 수강생 목록 조회 성공 테스트
        params: Dict[str, Any] = {"page": 1, "page_size": 10, "search": "홍길동", "status": "ACTIVATED"}

        response = self.client.get(self.url, data=params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        result = data["results"][0]
        self.assertEqual(result["id"], self.target_user.id)
        self.assertEqual(result["email"], self.target_user.email)
        self.assertEqual(result["name"], "홍길동")

    def test_get_student_list_unauthorized(self) -> None:
        # 401 에러 테스트
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        # 상태 코드 검증
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_student_list_permission_denied(self) -> None:
        # 403 에러 테스트
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))
        response = self.client.get(self.url)
        # 상태 코드 검증
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
