from datetime import timedelta
from typing import Any, cast

from django.contrib.auth.models import AbstractBaseUser
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.course_models import Course
from apps.subject.models.leaning_coach_models import LearningCoach
from apps.subject.models.traning_assistant_models import TrainingAssistant
from apps.users.choices import EnrollmentStatus, UserRole, UserStatus
from apps.users.models.models import User


class AdminUserRoleUpdateTest(TestCase):
    admin_user: User
    target_user: User
    cohort: Cohort
    course: Course
    client: APIClient
    url: str
    base_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.base_url = "/api/v1/admin/accounts/"
        user_manager: Any = User.objects

        # 관리자 생성
        cls.admin_user = user_manager.create(
            email="admin@example.com",
            nickname="admin97",
            name="관리자",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVATED,
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.admin_user.is_staff = True
        cls.admin_user.save()

        # 테스트 유저 생성
        cls.target_user = user_manager.create(
            email="user@example.com",
            nickname="user97",
            name="대상자",
            role=UserRole.USER,
            status=UserStatus.ACTIVATED,
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        # 강의 및 기수 생성
        cls.course = Course.objects.create(name="초격차 백엔드 부트캠프", tag="BE")

        now = timezone.now().date()
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=10,
            max_student=30,
            start_date=now,
            end_date=now + timedelta(days=90),
            status=EnrollmentStatus.PENDING,
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))
        self.url = f"{self.base_url}{self.target_user.id}/role/"

    def test_update_role_to_ta_success(self) -> None:
        """조교(TA) 권한 변경 테스트"""
        data = {"role": UserRole.TA, "cohort_id": self.cohort.id}
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 유저 권한 확인
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, UserRole.TA)

        # TA 테이블 데이터 확인
        self.assertTrue(TrainingAssistant.objects.filter(user=self.target_user, cohort=self.cohort).exists())

    def test_update_role_fail_400_bad_request(self) -> None:
        """400 Bad Request: 조교(TA) 변경 시 기수 정보가 없는 경우"""
        data = {"role": UserRole.TA}  # cohort_id 누락
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cohort_id", response.json()["error_detail"])
        self.assertEqual(
            response.json()["error_detail"]["cohort_id"][0], "조교 또는 수강생으로 변경 시 필수 필드입니다."
        )

    def test_update_role_fail_401_unauthorized(self) -> None:
        """401 Unauthorized: 로그인을 하지 않고 접근하는 경우"""
        self.client.force_authenticate(user=None)  # 인증 해제
        response = self.client.patch(self.url, data={"role": UserRole.STUDENT})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_role_fail_403_forbidden(self) -> None:
        """403 Forbidden: 관리자가 아닌 일반 유저가 권한 변경을 시도하는 경우"""
        # 관리자가 아닌 일반 유저(target_user)로 로그인 상태 변경
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))

        data = {"role": UserRole.TA, "cohort_id": self.cohort.id}
        response = self.client.patch(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_role_fail_404_not_found(self) -> None:
        """404 Not Found: 존재하지 않는 유저 ID(account_id)로 요청하는 경우"""
        invalid_url = f"{self.base_url}9999/role/"  # 존재하지 않는 ID 9999

        data = {"role": UserRole.TA, "cohort_id": self.cohort.id}
        response = self.client.patch(invalid_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
