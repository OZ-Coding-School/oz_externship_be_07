from datetime import timedelta
from typing import Any, Dict, cast

from django.contrib.auth.models import AbstractBaseUser
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.subject.models import Cohort, Course, EnrollmentRequest
from apps.users.models.models import User


class AdminUserEnrollmentTest(TestCase):
    admin_user: User
    target_user: User
    enrollment: EnrollmentRequest
    cohort: Cohort
    client: APIClient
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/admin/student-enrollments/"
        user_manager: Any = User.objects

        # 테스트 관리자 생성
        cls.admin_user = user_manager.create(
            email="admin@example.com",
            nickname="tadmin",
            name="관리자",
            role="ADMIN",
            status="ACTIVATED",
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.admin_user.is_staff = True
        cls.admin_user.save()

        # 테스트 유저 생성
        cls.target_user = user_manager.create(
            email="student@example.com",
            nickname="tstudent",
            name="홍길동",
            role="STUDENT",
            status="ACTIVATED",
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        course = Course.objects.create(name="초격차 백엔드 부트캠프", tag="BE")

        now = timezone.now().date()
        cls.cohort = Cohort.objects.create(
            course=course,
            number=10,
            max_student=30,
            start_date=now,
            end_date=now + timedelta(days=90),
            status="PENDING",
        )

        cls.enrollment = EnrollmentRequest.objects.create(user=cls.target_user, cohort=cls.cohort, status="PENDING")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def test_get_enrollment_list_success(self) -> None:
        """수강 신청 목록 조회 성공 테스트 (관리자 권한)"""
        params: Dict[str, Any] = {"page": 1, "page_size": 10}
        response = self.client.get(self.url, data=params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["count"], 1)
        result = data["results"][0]
        self.assertEqual(result["id"], self.enrollment.id)
        self.assertEqual(result["user"]["id"], self.target_user.id)
        self.assertEqual(result["user"]["name"], "홍길동")

    def test_get_enrollment_list_unauthorized(self) -> None:
        """401 Unauthorized 테스트"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_enrollment_list_permission_denied(self) -> None:
        """403 Forbidden 테스트"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
