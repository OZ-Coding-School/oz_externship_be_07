from __future__ import annotations

from datetime import date, datetime
from unittest.mock import patch

from django.db import IntegrityError
from django.http import Http404
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.views.cohort_admin_command_views import AdminCohortUpdateAPIView
from apps.users.models.models import User


class AdminCohortUpdateAPIViewTests(TestCase):
    admin_user: User
    normal_user: User
    course: Course
    cohort: Cohort
    factory: APIRequestFactory

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_user(
            email="admin_update@example.com",
            password="1234",
            name="관리자",
            nickname="admupdate",
            phone_number="01020001000",
            gender="MALE",
            birthday=date(2000, 1, 1),
            role="ADMIN",
        )
        cls.normal_user = User.objects.create_user(
            email="user_update@example.com",
            password="1234",
            name="일반유저",
            nickname="usrupdate",
            phone_number="01020002000",
            gender="FEMALE",
            birthday=date(2000, 1, 2),
            role="USER",
        )
        cls.course = Course.objects.create(
            name="코호트업데이트",
            tag="CU1",
            description="코호트 업데이트 과정",
        )
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=15,
            max_student=30,
            start_date=date(2025, 11, 1),
            end_date=date(2026, 4, 30),
            status="PREPARING",
        )

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_returns_200_when_request_is_valid(self) -> None:
        request = self.factory.patch(
            f"/api/v1/admin/cohorts/{self.cohort.id}",
            {
                "max_student": 40,
                "status": "IN_PROGRESS",
            },
            format="json",
        )
        force_authenticate(request, user=self.admin_user)

        updated_at = timezone.now()

        fake_updated_cohort = type(
            "FakeUpdatedCohort",
            (),
            {
                "id": self.cohort.id,
                "course_id": self.course.id,
                "number": 15,
                "max_student": 40,
                "start_date": date(2025, 11, 1),
                "end_date": date(2026, 4, 30),
                "status": "IN_PROGRESS",
                "updated_at": updated_at,
            },
        )()

        with patch(
            "apps.subject.views.cohort_admin_command_views.CohortService.update_cohort",
            return_value=fake_updated_cohort,
        ):
            response = AdminCohortUpdateAPIView.as_view()(request, cohort_id=self.cohort.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.cohort.id)
        self.assertEqual(response.data["course_id"], self.course.id)
        self.assertEqual(response.data["number"], 15)
        self.assertEqual(response.data["max_student"], 40)
        self.assertEqual(response.data["status"], "IN_PROGRESS")

    def test_returns_400_when_request_body_is_invalid(self) -> None:
        request = self.factory.patch(
            f"/api/v1/admin/cohorts/{self.cohort.id}",
            {
                "end_date": "2025-01-01",
            },
            format="json",
        )
        force_authenticate(request, user=self.admin_user)

        with patch(
            "apps.subject.views.cohort_admin_command_views.CohortUpdateRequestSerializer.is_valid",
            return_value=False,
        ), patch(
            "apps.subject.views.cohort_admin_command_views.CohortUpdateRequestSerializer.errors",
            new_callable=lambda: {
                "end_date": ["종료일은 시작일 이후여야 합니다."]
            },
        ):
            response = AdminCohortUpdateAPIView.as_view()(request, cohort_id=self.cohort.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "error_detail": {
                    "end_date": ["종료일은 시작일 이후여야 합니다."]
                }
            },
        )

    def test_returns_400_when_duplicate_cohort_number_exists(self) -> None:
        request = self.factory.patch(
            f"/api/v1/admin/cohorts/{self.cohort.id}",
            {
                "number": 99,
            },
            format="json",
        )
        force_authenticate(request, user=self.admin_user)

        with patch(
            "apps.subject.views.cohort_admin_command_views.CohortService.update_cohort",
            side_effect=IntegrityError,
        ):
            response = AdminCohortUpdateAPIView.as_view()(request, cohort_id=self.cohort.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "error_detail": {
                    "number": ["이미 해당 과정에 동일한 기수가 존재합니다."]
                }
            },
        )

    def test_returns_404_when_cohort_does_not_exist_before_serializer(self) -> None:
        request = self.factory.patch(
            "/api/v1/admin/cohorts/999999",
            {
                "max_student": 40,
            },
            format="json",
        )
        force_authenticate(request, user=self.admin_user)

        response = AdminCohortUpdateAPIView.as_view()(request, cohort_id=999999)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error_detail": "기수를 찾을 수 없습니다."})

    def test_returns_404_when_service_raises_http404(self) -> None:
        request = self.factory.patch(
            f"/api/v1/admin/cohorts/{self.cohort.id}",
            {
                "max_student": 40,
            },
            format="json",
        )
        force_authenticate(request, user=self.admin_user)

        with patch(
            "apps.subject.views.cohort_admin_command_views.CohortService.update_cohort",
            side_effect=Http404,
        ):
            response = AdminCohortUpdateAPIView.as_view()(request, cohort_id=self.cohort.id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error_detail": "기수를 찾을 수 없습니다."})

    def test_returns_403_when_user_is_not_staff(self) -> None:
        request = self.factory.patch(
            f"/api/v1/admin/cohorts/{self.cohort.id}",
            {
                "max_student": 40,
            },
            format="json",
        )
        force_authenticate(request, user=self.normal_user)

        response = AdminCohortUpdateAPIView.as_view()(request, cohort_id=self.cohort.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"error_detail": "권한이 없습니다."})

    def test_returns_401_when_user_is_not_authenticated(self) -> None:
        request = self.factory.patch(
            f"/api/v1/admin/cohorts/{self.cohort.id}",
            {
                "max_student": 40,
            },
            format="json",
        )

        response = AdminCohortUpdateAPIView.as_view()(request, cohort_id=self.cohort.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."})