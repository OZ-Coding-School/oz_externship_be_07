from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.choices import UserRole, UserStatus
from apps.users.models.models import User


class EnrollmentTrendAnalyticsAPITestCase(APITestCase):
    admin_user: User
    student: User
    course: Course
    cohort: Cohort
    now: datetime
    three_months_ago: datetime
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        # 관리자
        cls.admin_user = User.objects.create(
            email="admin@example.com",
            nickname="나는야",
            name="킹왕짱",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVATED,
            birthday="1990-01-01",
            phone_number="01000000000",
            is_staff=True,
        )

        # 유저
        cls.student = User.objects.create(
            email="student@test.com",
            nickname="나도야",
            name="킹왕짱",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVATED,
            birthday="2000-01-01",
            phone_number="01011111111",
        )

        # 과정
        cls.course = Course.objects.create(name="테스트 과정")

        # 기수
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=90),
        )

        cls.now = timezone.now()
        cls.three_months_ago = cls.now - timedelta(days=90)

        e1 = EnrollmentRequest.objects.create(user=cls.student, cohort=cls.cohort)
        e2 = EnrollmentRequest.objects.create(user=cls.student, cohort=cls.cohort)
        EnrollmentRequest.objects.filter(id__in=[e1.id, e2.id]).update(created_at=cls.three_months_ago)

        e3 = EnrollmentRequest.objects.create(user=cls.student, cohort=cls.cohort)
        EnrollmentRequest.objects.filter(id=e3.id).update(created_at=cls.now)

    def setUp(self) -> None:
        self.client = APIClient()

    def test_monthly_enrollment_trend_success(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin-student-enrollment-trends")

        response = self.client.get(url, {"interval": "monthly"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertEqual(data["interval"], "monthly")
        self.assertEqual(data["total"], 3)

        counts = [item["count"] for item in data["items"]]
        self.assertIn(0, counts)

        periods = [item["period"] for item in data["items"]]
        self.assertEqual(periods, sorted(periods))

    def test_interval_required(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin-student-enrollment-trends")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized(self) -> None:
        url = reverse("admin-student-enrollment-trends")
        response = self.client.get(url, {"interval": "monthly"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_not_admin(self) -> None:
        self.client.force_authenticate(user=self.student)
        url = reverse("admin-student-enrollment-trends")

        response = self.client.get(url, {"interval": "monthly"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
