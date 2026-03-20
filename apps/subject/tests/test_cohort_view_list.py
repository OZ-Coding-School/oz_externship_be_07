from __future__ import annotations

from datetime import date
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.subject.views.cohort_views import CohortListAPIView
from apps.users.models.models import User


class CohortListAPIViewTests(TestCase):
    staff_user: User
    normal_user: User
    factory: APIRequestFactory

    @classmethod
    def setUpTestData(cls) -> None:
        cls.staff_user = User.objects.create_user(
            email="staff_list@example.com",
            password="1234",
            name="관리자",
            nickname="stafflist",
            phone_number="01050001000",
            gender="MALE",
            birthday=date(2000, 1, 1),
            role="ADMIN",
        )
        cls.normal_user = User.objects.create_user(
            email="user_list@example.com",
            password="1234",
            name="일반유저",
            nickname="userlist",
            phone_number="01050002000",
            gender="FEMALE",
            birthday=date(2000, 1, 2),
            role="USER",
        )

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_returns_200_when_request_is_valid(self) -> None:
        request = self.factory.get("/api/v1/2/cohorts")
        force_authenticate(request, user=self.staff_user)

        fake_cohort_1 = type(
            "FakeCohort",
            (),
            {
                "id": 7,
                "course_id": 2,
                "number": 12,
                "status": "IN_PROGRESS",
            },
        )()
        fake_cohort_2 = type(
            "FakeCohort",
            (),
            {
                "id": 8,
                "course_id": 2,
                "number": 13,
                "status": "PREPARING",
            },
        )()

        with patch(
            "apps.subject.views.cohort_views.CohortService.get_cohorts_by_course_id",
            return_value=[fake_cohort_1, fake_cohort_2],
        ):
            response = CohortListAPIView.as_view()(request, course_id=2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    "id": 7,
                    "course_id": 2,
                    "number": 12,
                    "status": "IN_PROGRESS",
                },
                {
                    "id": 8,
                    "course_id": 2,
                    "number": 13,
                    "status": "PREPARING",
                },
            ],
        )

    def test_returns_403_when_user_is_not_allowed_to_view_list(self) -> None:
        request = self.factory.get("/api/v1/2/cohorts")
        force_authenticate(request, user=self.normal_user)

        response = CohortListAPIView.as_view()(request, course_id=2)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"error_detail": "이 리소스를 조회할 권한이 없습니다."})

    def test_returns_401_when_user_is_not_authenticated(self) -> None:
        request = self.factory.get("/api/v1/2/cohorts")

        response = CohortListAPIView.as_view()(request, course_id=2)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."})