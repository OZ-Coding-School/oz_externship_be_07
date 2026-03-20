from __future__ import annotations

from datetime import date
from unittest.mock import patch

from django.http import Http404
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.subject.views.cohort_admin_query_views import AdminCourseCohortAvgScoresAPIView
from apps.users.models.models import User


class AdminCourseCohortAvgScoresAPIViewTests(TestCase):
    admin_user: User
    normal_user: User
    factory: APIRequestFactory

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_user(
            email="admin_avg@example.com",
            password="1234",
            name="관리자",
            nickname="adminavg",
            phone_number="01030001000",
            gender="MALE",
            birthday=date(2000, 1, 1),
            role="ADMIN",
        )
        cls.normal_user = User.objects.create_user(
            email="user_avg@example.com",
            password="1234",
            name="일반유저",
            nickname="useravg",
            phone_number="01030002000",
            gender="FEMALE",
            birthday=date(2000, 1, 2),
            role="USER",
        )

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_returns_200_when_request_is_valid(self) -> None:
        request = self.factory.get("/api/v1/admin/courses/1/cohorts/avg-scores")
        force_authenticate(request, user=self.admin_user)

        expected = [
            {"name": "1기", "score": 40},
            {"name": "2기", "score": 12},
        ]

        with patch(
            "apps.subject.views.cohort_admin_query_views.CohortService.get_cohort_avg_scores",
            return_value=expected,
        ):
            response = AdminCourseCohortAvgScoresAPIView.as_view()(request, course_id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def test_returns_404_when_course_does_not_exist(self) -> None:
        request = self.factory.get("/api/v1/admin/courses/999/cohorts/avg-scores")
        force_authenticate(request, user=self.admin_user)

        with patch(
            "apps.subject.views.cohort_admin_query_views.CohortService.get_cohort_avg_scores",
            side_effect=Http404,
        ):
            response = AdminCourseCohortAvgScoresAPIView.as_view()(request, course_id=999)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error_detail": "과정을 찾을 수 없습니다."})

    def test_returns_403_when_user_is_not_staff(self) -> None:
        request = self.factory.get("/api/v1/admin/courses/1/cohorts/avg-scores")
        force_authenticate(request, user=self.normal_user)

        response = AdminCourseCohortAvgScoresAPIView.as_view()(request, course_id=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"error_detail": "권한이 없습니다."})

    def test_returns_401_when_user_is_not_authenticated(self) -> None:
        request = self.factory.get("/api/v1/admin/courses/1/cohorts/avg-scores")

        response = AdminCourseCohortAvgScoresAPIView.as_view()(request, course_id=1)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."})