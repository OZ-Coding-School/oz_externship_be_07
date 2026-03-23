from typing import cast

from django.contrib.auth.models import AbstractBaseUser
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.users.choices import UserRole, UserStatus
from apps.users.models.models import User


class AvailableCourseTest(TestCase):
    user: User
    course: Course
    active_cohort: Cohort
    inactive_cohort: Cohort
    client: APIClient
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트 코스 생성
        cls.url = "/api/v1/accounts/available-courses/"
        cls.course = Course.objects.create(name="초격차 백엔드 부트캠프")

        # 테스트 기수 생성 (신청 가능)
        cls.active_cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            status="PENDING",
            start_date="2026-03-01",
            end_date="2026-06-01",
        )
        # 테스트 기수 생성 (신청 불가능)
        cls.inactive_cohort = Cohort.objects.create(
            course=cls.course,
            number=2,
            max_student=30,
            status="FINISHED",
            start_date="2025-01-01",
            end_date="2025-04-01",
        )

        # 테스트 유저 생성
        cls.user = User.objects.create(
            email="student@example.com",
            nickname="테스트닉네임적기",
            name="귀찮다",
            birthday="1998-08-29",
            phone_number="01012345678",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVATED,
        )

    def setUp(self) -> None:
        self.client = APIClient()
        # 기본적으로는 인증된 상태로 시작
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.user))

    def test_get_available_courses_success_200(self) -> None:
        """200 OK: 로그인한 유저가 신청 가능한 기수 목록을 조회"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["cohort"]["id"], self.active_cohort.id)

    def test_get_available_courses_empty_list(self) -> None:
        """200 OK: 신청 가능한 기수가 없을 때 빈 리스트 반환 확인"""
        Cohort.objects.all().update(status="FINISHED")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_available_courses_fail_401_unauthorized(self) -> None:
        self.client.force_authenticate(user=None)
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")
