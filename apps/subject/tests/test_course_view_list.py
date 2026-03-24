from __future__ import annotations

from datetime import date
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.subject.views.course_views import CourseListAPIView
from apps.users.models.models import User


class CourseListAPIViewTests(TestCase):
    user: User
    factory: APIRequestFactory

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="user_course@example.com",
            password="1234",
            name="유저",
            nickname="usercourse",
            phone_number="01060001000",
            gender="MALE",
            birthday=date(2000, 1, 1),
            role="USER",
        )

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_returns_200_when_request_is_valid(self) -> None:
        request = self.factory.get("/api/v1/course/")
        force_authenticate(request, user=self.user)

        fake_course_1 = type(
            "FakeCourse",
            (),
            {
                "id": 1,
                "name": "14기 백엔드",
                "tag": "1",
                "thumbnail_img_url": "https://www.test.com",
            },
        )()
        fake_course_2 = type(
            "FakeCourse",
            (),
            {
                "id": 2,
                "name": "14기 프론트",
                "tag": "2",
                "thumbnail_img_url": "https://www.test.com",
            },
        )()

        with patch(
            "apps.subject.views.course_views.CourseService.get_course_list",
            return_value=[fake_course_1, fake_course_2],
        ):
            response = CourseListAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    "id": 1,
                    "name": "14기 백엔드",
                    "tag": "1",
                    "thumbnail_img_url": "https://www.test.com",
                },
                {
                    "id": 2,
                    "name": "14기 프론트",
                    "tag": "2",
                    "thumbnail_img_url": "https://www.test.com",
                },
            ],
        )

    def test_returns_401_when_user_is_not_authenticated(self) -> None:
        request = self.factory.get("/api/v1/course/")

        response = CourseListAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data,
            {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
        )
