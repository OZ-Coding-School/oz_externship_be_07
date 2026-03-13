import datetime

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.exam.models.choices import DeploymentStatus
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.choices import CohortStatus, SubjectStatus
from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.users.models.models import User


class ExamSubmissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            email="test@example.com",
            nickname="testuser",
            password="testpassword123",
            name="홍길동",
            phone_number="010-1234-5678",
            birthday="2000-09-25",
            gender="M",
            email_token="valid_email_token_123",
            sms_token="valid_sms_token_123",
        )

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

        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=40,
            start_date=datetime.date(2026, 1, 25),
            end_date=datetime.date(2026, 6, 25),
            status=CohortStatus.PENDING,
        )

        cls.exam = Exam.objects.create(
            title="testexam",
            subject=cls.subject,
            thumbnail_img="amazonaws.com/test_img_url",
        )

        cls.exam_deployment = ExamDeployment.objects.create(
            cohort=cls.cohort,
            exam=cls.exam,
            duration_time=60,
            access_code="test_access_code",
            open_at=datetime.datetime(2026, 3, 12, 13, 0, tzinfo=datetime.timezone.utc),
            close_at=datetime.datetime(2026, 3, 17, 16, 0, tzinfo=datetime.timezone.utc),
            questions_snapshot_json={"testquestion": "testquestion"},
            status=DeploymentStatus.ACTIVATED,
        )

        cls.exam_submission_data = ExamSubmission.objects.create(
            submitter=cls.user,
            deployment=cls.exam_deployment,
            started_at=datetime.datetime(2026, 3, 13, 23, 00, tzinfo=datetime.timezone.utc),
            cheating_count=1,
            answers_json={"testanswer": "testanswer"},
            score=50,
            correct_answer_count=2,
        )

    def setUp(self):
        self.client = APIClient()

    def test_search_submission_exam_success(self):
        data = self.exam_submission_data.copy()

        data["submitter"] = self.user
