import uuid
from datetime import date
from typing import Any

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.enrollment_request_models import EnrollmentRequest

User = get_user_model()


class MyCourseTest(APITestCase):
    user: Any
    course: Any
    cohort: Any
    url: str
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="eye@sick.com",
            nickname="눈아픈현오",
            phone_number=f"010{uuid.uuid4().hex[:8]}",
            password="password123",
            birthday="1998-08-12",
            gender="M",
        )
        cls.course = Course.objects.create(name="눈 피로 마사지", tag="TIP")
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 2, 1),
            status="PENDING",
        )
        EnrollmentRequest.objects.create(user=cls.user, cohort=cls.cohort)
        cls.url = reverse("users:me-enrolled-courses")

    def test_get_my_enrolled_courses_success(self)  -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["course"]["name"], "눈 피로 마사지")

    def test_get_my_enrolled_courses_unauthorized(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
