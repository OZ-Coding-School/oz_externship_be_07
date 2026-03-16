from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from apps.users.models.models import User
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.subject.models.cohort_models import Cohort
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.exam.servieces.exam_submission_services import ExamSubmissionService

class ExamSubmissionServiceTest(TestCase):
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
        """모든 위계 데이터를 순서대로 생성하여 AttributeError를 방지합니다."""
        now = timezone.now()

        # 1. User (필수: birthday)
        cls.user = User.objects.create_user(
            email="test@test.com",
            name="김철수",
            birthday="2000-01-01"
        )

        # 2. Course & Cohort (필수: max_student, start_date, end_date)
        cls.course = Course.objects.create(name="테스트코스", tag="TTC")
        cls.cohort = Cohort.objects.create(
            number=1,
            course=cls.course,
            max_student=30,
            start_date=now.date(),
            end_date=(now + timedelta(days=90)).date()
        )

        # 3. Subject (필수: number_of_days, number_of_hours)
        cls.subject = Subject.objects.create(
            title="테스트과목",
            course=cls.course,
            number_of_days=5,
            number_of_hours=40
        )

        # 4. Exam
        cls.exam = Exam.objects.create(title="테스트시험", subject=cls.subject)

        # 5. ExamDeployment (필수: open_at, close_at)
        cls.deployment = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort,
            status="Activated",
            duration_time=60,
            open_at=now,
            close_at=now + timedelta(days=1),
            access_code="TEST12",
            questions_snapshot_json="[]"  # 빈 리스트를 JSON 형태로 추가
        )

        # 6. ExamSubmission
        cls.submission = ExamSubmission.objects.create(
            submitter=cls.user,
            deployment=cls.deployment,
            started_at=now,
            cheating_count=0,
            answers_json="[]",
            correct_answer_count=0,  # 이번에 에러 난 필드!
            score=0                  # Failing row의 마지막 null 자리를 채우기 위한 필드
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