from __future__ import annotations

from datetime import date
from unittest.mock import patch

from django.http import Http404
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.subject.views.cohort_admin_query_views import AdminCohortStudentListAPIView
from apps.users.models.models import User


class AdminCohortStudentListAPIViewTests(TestCase):
    admin_user: User
    normal_user: User
    factory: APIRequestFactory

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_user(
            email="admin_students@example.com",
            password="1234",
            name="관리자",
            nickname="admstud",
            phone_number="01040001000",
            gender="MALE",
            birthday=date(2000, 1, 1),
            role="ADMIN",
        )
        cls.normal_user = User.objects.create_user(
            email="user_students@example.com",
            password="1234",
            name="일반유저",
            nickname="usrstud",
            phone_number="01040002000",
            gender="FEMALE",
            birthday=date(2000, 1, 2),
            role="USER",
        )

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_returns_200_when_request_is_valid(self) -> None:
        request = self.factory.get("/api/v1/admin/cohorts/1/students")
        force_authenticate(request, user=self.admin_user)

        fake_student_1 = type(
            "FakeCohortStudent",
            (),
            {"user": type("FakeUser", (), {"nickname": "ryuact", "name": "류액트"})()},
        )()
        fake_student_2 = type(
            "FakeCohortStudent",
            (),
            {"user": type("FakeUser", (), {"nickname": "kwonnode", "name": "권노드"})()},
        )()

        with patch(
            "apps.subject.views.cohort_admin_query_views.CohortService.get_cohort_students",
            return_value=[fake_student_1, fake_student_2],
        ):
            response = AdminCohortStudentListAPIView.as_view()(request, cohort_id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {"value": "ryuact", "label": "류액트"},
                {"value": "kwonnode", "label": "권노드"},
            ],
        )

    def test_returns_404_when_cohort_does_not_exist(self) -> None:
        request = self.factory.get("/api/v1/admin/cohorts/999/students")
        force_authenticate(request, user=self.admin_user)

        with patch(
            "apps.subject.views.cohort_admin_query_views.CohortService.get_cohort_students",
            side_effect=Http404,
        ):
            response = AdminCohortStudentListAPIView.as_view()(request, cohort_id=999)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error_detail": "기수를 찾을 수 없습니다."})

    def test_returns_403_when_user_is_not_staff(self) -> None:
        request = self.factory.get("/api/v1/admin/cohorts/1/students")
        force_authenticate(request, user=self.normal_user)

        response = AdminCohortStudentListAPIView.as_view()(request, cohort_id=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"error_detail": "권한이 없습니다."})

    def test_returns_401_when_user_is_not_authenticated(self) -> None:
        request = self.factory.get("/api/v1/admin/cohorts/1/students")

        response = AdminCohortStudentListAPIView.as_view()(request, cohort_id=1)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."})