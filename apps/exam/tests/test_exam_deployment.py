from datetime import timedelta
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.subject.models.choices import CohortStatus, SubjectStatus
from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject


class ExamDeploymentAPITest(APITestCase):
    course: Course
    subject: Subject
    exam: Exam
    cohort: Cohort
    cohort2: Cohort
    create_url: str
    deployment_data: Dict[str, Any]
    user: Any

    @classmethod
    def setUpTestData(cls) -> None:
        now = timezone.now()

        cls.course = Course.objects.create(
            name="testcourse",
            tag="tst",
            description="test",
            thumbnail_img_url="amazonaws.com/test_img_url",
        )

        cls.subject = Subject.objects.create(
            course=cls.course,
            title="testsubject",
            number_of_days=5,
            number_of_hours=40,
            thumbnail_img_url="amazonaws.com/test_img_url",
            status=SubjectStatus.ACTIVATED,
        )

        cls.exam = Exam.objects.create(
            title="testexam",
            subject=cls.subject,
            thumbnail_img_url="amazonaws.com/test_exam_img_url",
        )

        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=now.date(),
            end_date=(now + timedelta(days=100)).date(),
            status=CohortStatus.PENDING,
        )

        cls.cohort2 = Cohort.objects.create(
            course=cls.course,
            number=2,
            max_student=35,
            start_date=(now + timedelta(days=1)).date(),
            end_date=(now + timedelta(days=120)).date(),
            status=CohortStatus.PENDING,
        )

        cls.create_url = reverse("exam-deployment-list-create")

        cls.deployment_data = {
            "exam": cls.exam.pk,
            "cohort": cls.cohort.pk,
            "duration_time": 60,
            "open_at": (now + timedelta(hours=1)).isoformat(),
            "close_at": (now + timedelta(days=1)).isoformat(),
        }


    def _create_deployment(self, *, cohort_id: int | None = None) -> ExamDeployment:
        now = timezone.now()

        return ExamDeployment.objects.create(
            exam=self.exam,
            cohort=self.cohort if cohort_id is None else Cohort.objects.get(pk=cohort_id),
            duration_time=60,
            open_at=now + timedelta(hours=2),
            close_at=now + timedelta(days=2),
            access_code="TESTCODE1",
            questions_snapshot_json=[],
            status="Activated",
        )

    def test_create_exam_deployment_success(self) -> None:
        response = self.client.post(self.create_url, self.deployment_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExamDeployment.objects.count(), 1)
        self.assertIn("pk", response.data)

    def test_create_exam_deployment_fail_when_open_at_is_past(self) -> None:
        now = timezone.now()

        data = self.deployment_data.copy()
        data["open_at"] = (now - timedelta(hours=1)).isoformat()
        data["close_at"] = (now + timedelta(days=1)).isoformat()

        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_create_exam_deployment_fail_when_duplicated(self) -> None:
        self._create_deployment()

        response = self.client.post(self.create_url, self.deployment_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_get_exam_deployment_list_success(self) -> None:
        self._create_deployment(cohort_id=self.cohort.pk)
        self._create_deployment(cohort_id=self.cohort2.pk)

        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    def test_get_exam_deployment_detail_success(self) -> None:
        deployment = self._create_deployment()

        url = reverse("exam-deployment-detail", kwargs={"pk": deployment.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_exam_deployment_success(self) -> None:
        deployment = self._create_deployment()

        url = reverse("exam-deployment-detail", kwargs={"pk": deployment.pk})

        now = timezone.now()
        payload = {
            "duration_time": 90,
            "open_at": (now + timedelta(hours=3)).isoformat(),
            "close_at": (now + timedelta(days=3)).isoformat(),
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_exam_deployment_success(self) -> None:
        deployment = self._create_deployment()

        url = reverse("exam-deployment-detail", kwargs={"pk": deployment.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)