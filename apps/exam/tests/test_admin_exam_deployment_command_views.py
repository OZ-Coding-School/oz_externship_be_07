from datetime import date, timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.users.models.models import User


class TestAdminExamDeploymentCommandViews(APITestCase):
    url = "/api/v1/admin/exams/deployments"

    def setUp(self) -> None:
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="1234",
            name="관리자",
            nickname="admin",
            phone_number="01011112222",
            gender="MALE",
            birthday=date(1990, 1, 1),
            role="ADMIN",
        )

        self.user = User.objects.create_user(
            email="user@test.com",
            password="1234",
            name="유저",
            nickname="user",
            phone_number="01033334444",
            gender="FEMALE",
            birthday=date(1995, 1, 1),
            role="USER",
        )

        self.course = Course.objects.create(name="BE", tag="BE1")

        self.subject = Subject.objects.create(
            course=self.course,
            title="Python",
            number_of_days=10,
            number_of_hours=40,
        )

        self.exam = Exam.objects.create(
            subject=self.subject,
            title="시험",
        )

        today = date.today()
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=today,
            end_date=today + timedelta(days=90),
        )

        now = timezone.now()
        self.deployment = ExamDeployment.objects.create(
            exam=self.exam,
            cohort=self.cohort,
            duration_time=30,
            access_code="ABC123",
            open_at=now + timedelta(days=1),
            close_at=now + timedelta(days=1, hours=2),
            questions_snapshot_json=[],
            status="ACTIVATED",
        )

    def _time(self) -> tuple[str, str]:
        open_at = timezone.now() + timedelta(days=2)
        close_at = open_at + timedelta(hours=2)
        return open_at.strftime("%Y-%m-%d %H:%M:%S"), close_at.strftime("%Y-%m-%d %H:%M:%S")

    def test_create_success(self) -> None:
        self.client.force_authenticate(self.admin)

        new_cohort = Cohort.objects.create(
            course=self.course,
            number=2,
            max_student=30,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
        )

        open_at, close_at = self._time()

        res = self.client.post(
            self.url,
            {
                "exam_id": self.exam.id,
                "cohort_id": new_cohort.id,
                "duration_time": 30,
                "open_at": open_at,
                "close_at": close_at,
            },
            format="json",
        )

        self.assertEqual(res.status_code, 201)
        self.assertIn("pk", res.data)

    def test_create_duplicate_409(self) -> None:
        self.client.force_authenticate(self.admin)
        open_at, close_at = self._time()

        res = self.client.post(
            self.url,
            {
                "exam_id": self.exam.id,
                "cohort_id": self.cohort.id,
                "duration_time": 30,
                "open_at": open_at,
                "close_at": close_at,
            },
            format="json",
        )

        self.assertEqual(res.status_code, 409)

    def test_create_403(self) -> None:
        self.client.force_authenticate(self.user)
        open_at, close_at = self._time()

        res = self.client.post(
            self.url,
            {
                "exam_id": self.exam.id,
                "cohort_id": self.cohort.id,
                "duration_time": 30,
                "open_at": open_at,
                "close_at": close_at,
            },
            format="json",
        )

        self.assertEqual(res.status_code, 403)

    def test_update_success(self) -> None:
        self.client.force_authenticate(self.admin)

        open_at = timezone.now() + timedelta(days=3)
        close_at = open_at + timedelta(hours=3)

        res = self.client.patch(
            f"{self.url}/{self.deployment.id}",
            {
                "duration_time": 50,
                "open_at": open_at.strftime("%Y-%m-%d %H:%M:%S"),
                "close_at": close_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            format="json",
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["deployment_id"], self.deployment.id)

    def test_status_update(self) -> None:
        self.client.force_authenticate(self.admin)

        res = self.client.patch(
            f"{self.url}/{self.deployment.id}/status",
            {"status": "deactivated"},
            format="json",
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "deactivated")

    def test_delete(self) -> None:
        self.client.force_authenticate(self.admin)

        res = self.client.delete(f"{self.url}/{self.deployment.id}")

        self.assertEqual(res.status_code, 200)
        self.assertFalse(ExamDeployment.objects.filter(id=self.deployment.id).exists())

    def test_create_invalid_request_400(self) -> None:
        self.client.force_authenticate(self.admin)

        open_at = timezone.now() + timedelta(days=2)
        close_at = open_at - timedelta(hours=1)

        res = self.client.post(
            self.url,
            {
                "exam_id": self.exam.id,
                "cohort_id": self.cohort.id,
                "duration_time": 30,
                "open_at": open_at.strftime("%Y-%m-%d %H:%M:%S"),
                "close_at": close_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            format="json",
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error_detail"], "유효하지 않은 배포 생성 요청입니다.")

    def test_update_invalid_request_400(self) -> None:
        self.client.force_authenticate(self.admin)

        open_at = timezone.now() + timedelta(days=3)
        close_at = open_at - timedelta(hours=1)

        res = self.client.patch(
            f"{self.url}/{self.deployment.id}",
            {
                "duration_time": 50,
                "open_at": open_at.strftime("%Y-%m-%d %H:%M:%S"),
                "close_at": close_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            format="json",
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error_detail"], "유효하지 않은 배포 수정 요청입니다.")

    def test_status_update_invalid_request_400(self) -> None:
        self.client.force_authenticate(self.admin)

        res = self.client.patch(
            f"{self.url}/{self.deployment.id}/status",
            {"status": "invalid-status"},
            format="json",
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error_detail"], "유효하지 않은 배포 상태 요청입니다.")
