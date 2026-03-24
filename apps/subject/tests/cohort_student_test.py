from datetime import date, timedelta
from typing import Any

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.choices import CohortStatus, SubjectStatus
from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.users.models.models import User


class CohortStudentAPITest(APITestCase):
    """Cohort Student API 테스트"""

    admin_user: User
    student_user: User
    course: Course
    cohort: Cohort
    subject: Subject
    list_url: str
    score_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        """테스트 전체에서 공통으로 사용할 데이터 생성"""

        user_manager: Any = User.objects

        cls.admin_user = user_manager.create(
            email="admin@example.com",
            nickname="tadmin",
            name="관리자",
            role="ADMIN",
            status="ACTIVATED",
            birthday="1990-01-01",
            phone_number="01000000000",
        )
        cls.admin_user.is_staff = True
        cls.admin_user.save()

        cls.student_user = user_manager.create(
            email="student@example.com",
            nickname="tstudent",
            name="홍길동",
            role="ST",
            status="ACTIVATED",
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        cls.course = Course.objects.create(
            name="testcourse",
            tag="tst",
            description="test",
            thumbnail_img_url="amazonaws.com/test_img_url",
        )

        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 1),
            status=CohortStatus.PREPARING,
        )

        cls.subject = Subject.objects.create(
            course=cls.course,
            title="HTML/CSS",
            number_of_days=5,
            number_of_hours=40,
            thumbnail_img_url="amazonaws.com/test_subject_img",
            status=SubjectStatus.ACTIVATED,
        )

        exam = Exam.objects.create(
            title="HTML 시험",
            subject=cls.subject,
            thumbnail_img_url="amazonaws.com/test_exam_img",
        )

        now = timezone.now()

        deployment = ExamDeployment.objects.create(
            cohort=cls.cohort,
            exam=exam,
            duration_time=60,
            access_code="HTML1234",
            open_at=now,
            close_at=now + timedelta(hours=2),
            questions_snapshot_json={
                "exam_id": exam.id,
                "questions": [],
            },
        )

        ExamSubmission.objects.create(
            submitter=cls.student_user,
            deployment=deployment,
            started_at=now,
            cheating_count=0,
            answers_json={"answers": []},
            score=85,
            correct_answer_count=8,
        )

        cls.list_url = reverse("student-list")
        cls.score_url = reverse(
            "student-score",
            kwargs={"student_id": cls.student_user.pk},
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_student_scores_success(self) -> None:
        """학생별 과목 점수 조회 성공 테스트"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.score_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["subject"], "HTML/CSS")
        self.assertEqual(response.data[0]["score"], 85)

    def test_get_student_scores_unauthorized_denied(self) -> None:
        """학생별 과목 점수 조회 401 테스트"""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.score_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_get_student_scores_permission_denied(self) -> None:
        """학생별 과목 점수 조회 403 테스트"""
        non_admin_user = User.objects.create(
            email="nonadmin@example.com",
            nickname="tnonadmin",
            name="일반유저",
            role="ST",
            status="ACTIVATED",
            birthday="1999-01-01",
            phone_number="01099998888",
        )

        self.client.force_authenticate(user=non_admin_user)

        response = self.client.get(self.score_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_get_student_scores_not_found(self) -> None:
        """학생별 과목 점수 조회 404 테스트"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("student-score", kwargs={"student_id": 9999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "학생을 찾을 수 없습니다.")
