import json
from typing import Any, cast

from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion
from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.choices import SubjectStatus
from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.users.models.models import User


class ExamSubmissionAPITest(APITestCase):
    admin_user: User
    student_user: User
    other_student_user: User
    course: Course
    subject: Subject
    exam: Exam
    deployment: ExamDeployment
    question: ExamQuestion
    cohort: Cohort
    submission: ExamSubmission
    submission_data: dict[str, Any]
    list_url: str

    @classmethod
    def setUpTestData(cls) -> None:
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
            role="STUDENT",
            status="ACTIVATED",
            birthday="1998-08-29",
            phone_number="01012345678",
        )

        cls.other_student_user = user_manager.create(
            email="other@example.com",
            nickname="tother",
            name="김철수",
            role="STUDENT",
            status="ACTIVATED",
            birthday="1999-03-15",
            phone_number="01087654321",
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
        cls.exam = Exam.objects.create(
            title="testexam",
            subject_id=cls.subject.pk,
            thumbnail_img_url="amazonaws.com/test_img_url",
        )
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date="2025-01-01",
            end_date="2025-12-31",
        )
        cls.deployment = ExamDeployment.objects.create(
            cohort=cls.cohort,
            exam=cls.exam,
            duration_time=60,
            access_code="testcode1234",
            open_at="2025-01-01T00:00:00Z",
            close_at="2025-12-31T23:59:59Z",
            questions_snapshot_json=[],
        )
        cls.question = ExamQuestion.objects.create(
            exam=cls.exam,
            question="testquestion",
            prompt="testprompt",
            blank_count=0,
            options_json=json.dumps(
                ["정적 타이핑 언어", "인터프리터 언어", "컴파일 방식만을 지원", "메모리 직접 관리 필요"]
            ),
            type="SINGLE_CHOICE",
            answer=["정적 타이핑 언어"],
            point=10,
            explanation="testexplanation",
        )
        cls.submission_data = {
            "deployment_id": cls.deployment.pk,
            "started_at": "2025-02-01T11:20:00",
            "cheating_count": 0,
            "answers": [
                {
                    "question_id": cls.question.pk,
                    "type": "single_choice",
                    "submitted_answer": "정적 타이핑 언어",
                },
            ],
        }

        cls.list_url = reverse("exam-submission-create")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.student_user))

    def test_create_submission_success(self) -> None:
        """쪽지시험 제출 성공 테스트 (POST)"""
        data = self.submission_data.copy()

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("submission_id", response.data)
        self.assertIn("score", response.data)
        self.assertIn("correct_answer_count", response.data)
        self.assertIn("redirect_url", response.data)
        self.assertEqual(response.data["redirect_url"], f"/exam/result/{response.data['submission_id']}")

    def test_create_submission_missing_field_bad_request(self) -> None:
        """쪽지시험 제출 400 에러 : 필수 필드(deployment_id) 누락 시 실패 테스트"""
        data = {
            "started_at": "2025-02-01T11:20:00",
            "cheating_count": 0,
            "answers": [],
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "유효하지 않은 시험 응시 세션입니다.")

    def test_create_submission_unauthorized_denied(self) -> None:
        """쪽지시험 제출 401 에러코드 테스트"""
        data = self.submission_data.copy()
        self.client.force_authenticate(user=None)

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_create_submission_deployment_not_found(self) -> None:
        """쪽지시험 제출 404 에러 코드 테스트 : 존재하지 않는 deployment_id"""
        data = self.submission_data.copy()
        data["deployment_id"] = 99999

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "해당 시험 정보를 찾을 수 없습니다.")

    def test_create_submission_already_submitted_conflict(self) -> None:
        """쪽지시험 제출 409 에러 코드 테스트 : 이미 제출한 시험 재제출 시"""
        data = self.submission_data.copy()

        self.client.post(self.list_url, data, format="json")

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error_detail"], "이미 제출된 시험입니다.")

    def _get_detail_url(self, submission_id: int) -> str:
        return reverse("exam-submission-detail", kwargs={"submission_id": submission_id})

    def _create_submission(self) -> ExamSubmission:
        """테스트용 제출 데이터 생성 헬퍼"""
        return ExamSubmission.objects.create(
            submitter=self.student_user,
            deployment=self.deployment,
            cheating_count=0,
            answers_json=[
                {
                    "question_id": self.question.pk,
                    "type": "single_choice",
                    "submitted_answer": "정적 타이핑 언어",
                }
            ],
            score=10,
            correct_answer_count=1,
            started_at="2025-02-01T11:20:00Z",
        )

    def test_get_submission_detail_success(self) -> None:
        """쪽지시험 결과 확인 성공 테스트 (GET)"""
        submission = self._create_submission()
        url = self._get_detail_url(submission.pk)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], submission.pk)
        self.assertEqual(response.data["submitter_id"], self.student_user.pk)
        self.assertEqual(response.data["deployment_id"], self.deployment.pk)
        self.assertIn("exam", response.data)
        self.assertIn("questions", response.data)
        self.assertIn("total_score", response.data)  # API 응답 필드명은 total_score
        self.assertIn("correct_answer_count", response.data)
        self.assertIn("elapsed_time", response.data)
        self.assertIn("started_at", response.data)
        self.assertIn("submitted_at", response.data)  # TimeStampModel의 created_at을 매핑

    def test_get_submission_detail_response_fields(self) -> None:
        """쪽지시험 결과 응답 내 questions 필드 구조 검증"""
        submission = self._create_submission()
        url = self._get_detail_url(submission.pk)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["questions"], list)

        if response.data["questions"]:
            question_data = response.data["questions"][0]
            self.assertIn("id", question_data)
            self.assertIn("question", question_data)
            self.assertIn("type", question_data)
            self.assertIn("answer", question_data)
            self.assertIn("point", question_data)
            self.assertIn("is_correct", question_data)
            self.assertIn("submitted_answer", question_data)
            self.assertIn("explanation", question_data)

    def test_get_submission_detail_unauthorized_denied(self) -> None:
        """쪽지시험 결과 확인 401 에러코드 테스트"""
        submission = self._create_submission()
        url = self._get_detail_url(submission.pk)
        self.client.force_authenticate(user=None)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_get_submission_detail_permission_denied(self) -> None:
        """쪽지시험 결과 확인 403 에러 코드 테스트 : 다른 유저의 제출 결과 조회"""
        submission = self._create_submission()
        url = self._get_detail_url(submission.pk)
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.other_student_user))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_get_submission_detail_not_found(self) -> None:
        """쪽지시험 결과 확인 404 에러 코드 테스트 : 존재하지 않는 submission_id"""
        url = self._get_detail_url(99999)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "해당 시험 정보를 찾을 수 없습니다.")
