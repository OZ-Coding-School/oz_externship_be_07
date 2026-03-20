from __future__ import annotations

from datetime import date
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.subject.views.cohort_admin_command_views import AdminCohortCreateAPIView
from apps.users.models.models import User


class AdminCohortCreateAPIViewTests(TestCase):
    admin_user: User
    normal_user: User
    factory: APIRequestFactory

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_user(
            email="admin_create@example.com",
            password="1234",
            name="관리자",
            nickname="admcreate",
            phone_number="01010001000",
            gender="MALE",
            birthday=date(2000, 1, 1),
            role="ADMIN",
        )
        cls.normal_user = User.objects.create_user(
            email="user_create@example.com",
            password="1234",
            name="일반유저",
            nickname="usrcreate",
            phone_number="01010002000",
            gender="FEMALE",
            birthday=date(2000, 1, 2),
            role="USER",
        )

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_returns_201_when_request_is_valid(self) -> None:
        request = self.factory.post(
            "/api/v1/admin/cohorts",
            {
                "course_id": 1,
                "number": 15,
                "max_student": 30,
                "start_date": "2025-11-01",
                "end_date": "2026-04-30",
                "status": "PREPARING",
            },
            format="json",
        )
        force_authenticate(request, user=self.admin_user)

        fake_cohort = type("FakeCohort", (), {"id": 123})()

        with patch(
            "apps.subject.views.cohort_admin_command_views.CohortCreateRequestSerializer.is_valid",
            return_value=True,
        ), patch(
            "apps.subject.views.cohort_admin_command_views.CohortCreateRequestSerializer.validated_data",
            new_callable=lambda: {
                "course": object(),
                "number": 15,
                "max_student": 30,
                "start_date": date(2025, 11, 1),
                "end_date": date(2026, 4, 30),
                "status": "PREPARING",
            },
        ), patch(
            "apps.subject.views.cohort_admin_command_views.CohortService.create_cohort",
            return_value=fake_cohort,
        ):
            response = AdminCohortCreateAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "detail": "기수가 등록되었습니다.",
                "id": 123,
            },
        )

    def test_returns_400_when_request_body_is_invalid(self) -> None:
        request = self.factory.post(
            "/api/v1/admin/cohorts",
            {},
            format="json",
        )
        force_authenticate(request, user=self.admin_user)

        with patch(
            "apps.subject.views.cohort_admin_command_views.CohortCreateRequestSerializer.is_valid",
            return_value=False,
        ), patch(
            "apps.subject.views.cohort_admin_command_views.CohortCreateRequestSerializer.errors",
            new_callable=lambda: {
                "course_id": ["이 필드는 필수 항목입니다."],
            },
        ):
            response = AdminCohortCreateAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "error_detail": {
                    "course_id": ["이 필드는 필수 항목입니다."],
                }
            },
        )

    def test_returns_400_when_duplicate_cohort_number_exists(self) -> None:
        request = self.factory.post(
            "/api/v1/admin/cohorts",
            {
                "course_id": 1,
                "number": 15,
                "max_student": 30,
                "start_date": "2025-11-01",
                "end_date": "2026-04-30",
            },
            format="json",
        )
        force_authenticate(request, user=self.admin_user)

        with patch(
            "apps.subject.views.cohort_admin_command_views.CohortCreateRequestSerializer.is_valid",
            return_value=True,
        ), patch(
            "apps.subject.views.cohort_admin_command_views.CohortCreateRequestSerializer.validated_data",
            new_callable=lambda: {
                "course": object(),
                "number": 15,
                "max_student": 30,
                "start_date": date(2025, 11, 1),
                "end_date": date(2026, 4, 30),
            },
        ), patch(
            "apps.subject.views.cohort_admin_command_views.CohortService.create_cohort",
            side_effect=IntegrityError,
        ):
            response = AdminCohortCreateAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "error_detail": {
                    "number": ["이미 해당 과정에 동일한 기수가 존재합니다."]
                }
            },
        )

    def test_returns_403_when_user_is_not_staff(self) -> None:
        request = self.factory.post(
            "/api/v1/admin/cohorts",
            {
                "course_id": 1,
                "number": 15,
                "max_student": 30,
                "start_date": "2025-11-01",
                "end_date": "2026-04-30",
            },
            format="json",
        )
        force_authenticate(request, user=self.normal_user)

        response = AdminCohortCreateAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"error_detail": "권한이 없습니다."})

    def test_returns_401_when_user_is_not_authenticated(self) -> None:
        request = self.factory.post(
            "/api/v1/admin/cohorts",
            {
                "course_id": 1,
                "number": 15,
                "max_student": 30,
                "start_date": "2025-11-01",
                "end_date": "2026-04-30",
            },
            format="json",
        )

        response = AdminCohortCreateAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."})