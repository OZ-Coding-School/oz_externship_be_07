from datetime import timedelta
from typing import Any, Dict, List, cast

from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.models.models import User


class AdminEnrollmentAcceptTest(APITestCase):
    admin_user: User
    user: User
    course: Course
    cohort: Cohort
    enroll1: EnrollmentRequest
    enroll2: EnrollmentRequest
    already_approved: EnrollmentRequest
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        user_manager: Any = User.objects

        # 유저 생성
        cls.admin_user = user_manager.create_user(
            email="admin@example.com",
            password="password123",
            role="ADMIN",
            name="관리자",
            nickname="admin99",
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.user = user_manager.create_user(
            email="student@example.com",
            password="password123",
            role="USER",
            name="학생",
            nickname="student99",
            birthday="1995-05-05",
            phone_number="01012345678",
        )

        # 강의 및 기수 생성
        cls.course = Course.objects.create(name="백엔드 코스", tag="BE")
        now = timezone.now().date()
        cls.cohort = Cohort.objects.create(
            number=1,
            course=cls.course,
            max_student=30,
            start_date=now,
            end_date=now + timedelta(days=90),
            status="PENDING",
        )

        # 신청 데이터 생성
        cls.enroll1 = EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort, status="PENDING")
        cls.enroll2 = EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort, status="PENDING")
        cls.already_approved = EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort, status="ACCEPTED")

        cls.url = reverse("admin-enrollment-accept")

    def setUp(self) -> None:
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def test_accept_enrollments_success(self) -> None:
        """정상적인 승인 요청 테스트"""
        data: Dict[str, List[int]] = {"enrollments": [self.enroll1.id, self.enroll2.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "2건의 수강 신청이 승인되었습니다.")

        # DB 반영 확인
        self.enroll1.refresh_from_db()
        self.enroll2.refresh_from_db()
        self.assertEqual(self.enroll1.status, "ACCEPTED")
        self.assertEqual(self.enroll2.status, "ACCEPTED")

    def test_accept_enrollments_empty_list(self) -> None:
        """빈 리스트 요청 시 시리얼라이저 에러 확인 (400)"""
        data: Dict[str, List[Any]] = {"enrollments": []}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("enrollments", response.data["error_detail"])

    def test_accept_enrollments_fail_already_approved(self) -> None:
        """이미 승인된 건에 대해 요청 시 400 에러 확인"""
        data: Dict[str, List[int]] = {"enrollments": [self.already_approved.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("승인 가능한 대기 상태의 신청 건이 없습니다.", str(response.data.get("error_detail", "")))

    def test_accept_enrollments_permission_denied(self) -> None:
        """일반 유저가 요청 시 403 에러 확인"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))

        data: Dict[str, List[int]] = {"enrollments": [self.enroll1.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
