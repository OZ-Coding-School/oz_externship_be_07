from typing import Any, cast

from django.contrib.auth.models import AbstractBaseUser
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.course_models import Course
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.choices import EnrollmentStatus, UserRole, UserStatus
from apps.users.models.models import User


class EnrollStudentTest(TestCase):
    client: APIClient
    user: User
    base_url = "/api/v1/accounts/enroll-student/"
    cohort: Cohort
    course: Course

    @classmethod
    def setUpTestData(cls) -> None:
        cls.course = Course.objects.create(name="Python 백엔드 과정")

        # 테스트 유저 생성
        cls.user = User.objects.create(
            email="student@example.com",
            nickname="뽀로로와",
            name="친구들",
            phone_number="01012345678",
            gender="M",
            birthday="2000-01-01",
            role=UserRole.USER,
            status=UserStatus.ACTIVATED,
        )

        # 테스트 기수 생성
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=3,
            max_student=30,
            start_date="2026-03-01",
            end_date="2026-06-01",
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_enroll_student_success_201(self) -> None:
        """201 Created: 정상적인 기수 등록 신청"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))

        data: dict[str, Any] = {"cohort_id": self.cohort.id}
        response = self.client.post(self.base_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(EnrollmentRequest.objects.filter(user=self.user, cohort=self.cohort).exists())
        self.assertFalse(CohortStudent.objects.filter(user=self.user, cohort=self.cohort).exists())

    def test_enroll_student_fail_already_pending(self) -> None:
        """400 Bad Request: 대기 중인 신청이 있을 때"""
        EnrollmentRequest.objects.create(user=self.user, cohort=self.cohort, status=EnrollmentStatus.PENDING)

        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))
        response = self.client.post(self.base_url, data={"cohort_id": self.cohort.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"]["detail"][0], "이미 신청한 기수입니다.")

    def test_enroll_student_fail_already_accepted(self) -> None:
        """400 Bad Request: 이미 승인된 신청(수강 중)이 있을 때"""
        EnrollmentRequest.objects.create(user=self.user, cohort=self.cohort, status=EnrollmentStatus.ACCEPTED)

        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))
        response = self.client.post(self.base_url, data={"cohort_id": self.cohort.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"]["detail"][0], "이미 등록된 기수입니다.")

    def test_enroll_student_fail_401_unauthorized(self) -> None:
        """401 Unauthorized: 로그인하지 않은 상태로 요청"""
        data = {"cohort_id": self.cohort.id}
        response = self.client.post(self.base_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")
