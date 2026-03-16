from datetime import timedelta
from typing import Any

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.exam.servieces.exam_submission_services import ExamSubmissionService
from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.users.models.models import User


class ExamSubmissionServiceTest(APITestCase):
    # 속성 타입 선언 (mypy 에러 방지)
    user: User
    course: Course
    cohort: Cohort
    subject: Subject
    exam: Exam
    deployment: ExamDeployment
    submission: ExamSubmission

    @classmethod
    def setUpTestData(cls) -> None:
        # self.client = APIClient()  <-- 이 줄을 삭제했습니다. (mypy 에러 원인)

        """모든 위계 데이터를 순서대로 생성하여 AttributeError를 방지합니다."""
        now = timezone.now()

        # 1. User (필수: birthday)
        cls.user = User.objects.create_user(email="test@test.com", name="김철수", birthday="2000-01-01")

        # ... 이하 데이터 생성 로직 동일 ...
        cls.course = Course.objects.create(name="테스트코스", tag="TTC")
        cls.cohort = Cohort.objects.create(
            number=1,
            course=cls.course,
            max_student=30,
            start_date=now.date(),
            end_date=(now + timedelta(days=90)).date(),
        )
        cls.subject = Subject.objects.create(
            title="테스트과목", course=cls.course, number_of_days=5, number_of_hours=40
        )
        cls.exam = Exam.objects.create(title="테스트시험", subject=cls.subject)
        cls.deployment = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort,
            status="Activated",
            duration_time=60,
            open_at=now,
            close_at=now + timedelta(days=1),
            access_code="TEST12",
            questions_snapshot_json="[]",
        )
        cls.submission = ExamSubmission.objects.create(
            submitter=cls.user,
            deployment=cls.deployment,
            started_at=now,
            cheating_count=0,
            answers_json="[]",
            correct_answer_count=0,
            score=0,
        )

    def test_get_submission_list_success(self) -> None:
        queryset = ExamSubmissionService.get_submission_list()
        self.assertEqual(queryset.count(), 1)

    def test_get_submission_list_search_success(self) -> None:
        queryset = ExamSubmissionService.get_submission_list(search_keyword="철수")
        self.assertEqual(queryset.count(), 1)

    def test_delete_submission_success(self) -> None:
        submission_id = self.submission.pk
        deleted_id = ExamSubmissionService.delete_submission(submission_id)
        self.assertEqual(deleted_id, submission_id)
        self.assertFalse(ExamSubmission.objects.filter(id=submission_id).exists())

    def test_get_submission_list_without_keyword(self) -> None:
        """검색어가 없을 때 전체 리스트를 반환하는지 검증"""
        # 서비스 로직에서 search_keyword=None 일 때의 분기를 체크합니다.
        queryset = ExamSubmissionService.get_submission_list(search_keyword=None)
        self.assertEqual(queryset.count(), 1)

        ## --- View 테스트 (config 기반 최종 교정본) ---

    def test_list_view_success(self: Any) -> None:
        self.client.force_authenticate(user=self.user)  # 인증 추가
        url: str = "/api/v1/admin/exams/submissions"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_view_success(self: Any) -> None:
        self.client.force_authenticate(user=self.user)  # 인증 추가
        url: str = f"/api/v1/admin/exams/submissions/{self.submission.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_view_success(self: Any) -> None:
        self.client.force_authenticate(user=self.user)  # 인증 추가
        url: str = f"/api/v1/admin/exams/submissions/{self.submission.pk}"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_view_404(self: Any) -> None:
        self.client.force_authenticate(user=self.user)  # 인증 추가
        url: str = "/api/v1/admin/exams/submissions/9999"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
