from typing import Any, cast

from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.subject.models import Cohort, CohortStudent, Course
from apps.users.models import User


class StudentManagementTests(APITestCase):
    def setUp(self) -> None:
        self.course = Course.objects.create(name="초격차 백엔드", tag="BE")
        self.cohort = Cohort.objects.create(course=self.course, number=10)

        self.student = User.objects.create(
            email="test@example.com", nickname="코딩왕김오즈", name="김오즈", role="USER", status="ACTIVATED"
        )

        CohortStudent.objects.create(user=self.student, cohort=self.cohort)

        # 3. 관리자 계정 생성
        self.admin_user = User.objects.create(
            email="admin@example.com",
            nickname="관리자",
            role="ADMIN",
        )
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

        # 4. URL 설정
        self.url = reverse("admin-students-list")

    def test_admin_can_get_student_list_with_course_data(self) -> None:

        # 실행
        response = self.client.get(self.url)

        # HTTP 상태 코드 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 페이지네이션 구조 검증
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

        # 중첩된 객체 구조 검증
        user_data = response.data["results"][0]
        self.assertEqual(user_data["email"], "student@example.com")

        # in_progress_course 구조 검증
        in_progress = user_data.get("in_progress_course")
        self.assertIsNotNone(in_progress)
        self.assertEqual(in_progress["cohort"]["number"], 10)
        self.assertEqual(in_progress["course"]["name"], "초격차 백엔드")
        self.assertEqual(in_progress["course"]["tag"], "BE")

    def test_unauthorized_access_returns_401(self) -> None:
        # 인증 없이 접근 시 401 에러가 나오는지 확인
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_access_returns_403(self) -> None:
        # 일반 유저가 접근 시 403 에러가 나오는지 확인
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.student))
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
