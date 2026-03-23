from datetime import date, timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.cohort_models import Cohort
from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.users.models.models import User


class TestAdminExamDeploymentQueryViews(APITestCase):
    url = "/api/v1/admin/exams/deployments"

    def setUp(self) -> None:
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="1234",
            name="관리자",
            nickname="adminq",
            phone_number="01055556666",
            gender="MALE",
            birthday=date(1990, 1, 1),
            role="ADMIN",
        )

        self.user = User.objects.create_user(
            email="user@test.com",
            password="1234",
            name="유저",
            nickname="userq",
            phone_number="01077778888",
            gender="FEMALE",
            birthday=date(1995, 1, 1),
            role="USER",
        )

        self.student1 = User.objects.create_user(
            email="s1@test.com",
            password="1234",
            name="학생1",
            nickname="s1",
            phone_number="01011110000",
            gender="MALE",
            birthday=date(2000, 1, 1),
            role="USER",
        )

        self.student2 = User.objects.create_user(
            email="s2@test.com",
            password="1234",
            name="학생2",
            nickname="s2",
            phone_number="01022220000",
            gender="FEMALE",
            birthday=date(2000, 1, 1),
            role="USER",
        )

        self.course = Course.objects.create(name="BE", tag="BEQ")
        self.subject = Subject.objects.create(
            course=self.course,
            title="Python",
            number_of_days=10,
            number_of_hours=40,
        )

        self.exam = Exam.objects.create(subject=self.subject, title="시험")

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
            access_code="CODE123",
            open_at=now + timedelta(days=1),
            close_at=now + timedelta(days=1, hours=2),
            questions_snapshot_json=[],
            status="ACTIVATED",
        )

        CohortStudent.objects.create(cohort=self.cohort, user=self.student1)
        CohortStudent.objects.create(cohort=self.cohort, user=self.student2)

        ExamSubmission.objects.create(
            submitter=self.student1,
            deployment=self.deployment,
            started_at=timezone.now(),
            cheating_count=0,
            answers_json={},
            score=80,
            correct_answer_count=8,
        )

    def test_list_success(self) -> None:
        self.client.force_authenticate(self.admin)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.data["count"], 1)

    def test_list_403(self) -> None:
        self.client.force_authenticate(self.user)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, 403)

    def test_detail_success(self) -> None:
        self.client.force_authenticate(self.admin)

        res = self.client.get(f"{self.url}/{self.deployment.id}")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["submit_count"], 1)
        self.assertEqual(res.data["not_submitted_count"], 1)

    def test_detail_404(self) -> None:
        self.client.force_authenticate(self.admin)

        res = self.client.get(f"{self.url}/9999")

        self.assertEqual(res.status_code, 404)

    def test_detail_403(self) -> None:
        self.client.force_authenticate(self.user)

        res = self.client.get(f"{self.url}/{self.deployment.id}")

        self.assertEqual(res.status_code, 403)
