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


class ExamAdminSubmissionAPITest(APITestCase):
    admin_user: User
    student_user: User
    course: Course
    subject: Subject
    exam: Exam
    cohort: Cohort
    deployment: ExamDeployment
    question: ExamQuestion
    submission: ExamSubmission
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
            questions_snapshot_json=[
                {
                    "id": 1,
                    "answer": ["정적 타이핑 언어"],
                    "point": 10,
                    "type": "SINGLE_CHOICE",
                    "question": "testquestion",
                    "prompt": "testprompt",
                    "options": ["정적 타이핑 언어", "인터프리터 언어", "컴파일 방식만을 지원", "메모리 직접 관리 필요"],
                    "explanation": "testexplanation",
                    "blank_count": 0,
                }
            ],
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
        cls.submission = ExamSubmission.objects.create(
            submitter=cls.student_user,
            deployment=cls.deployment,
            cheating_count=0,
            answers_json=[
                {
                    "question_id": cls.question.pk,
                    "type": "single_choice",
                    "submitted_answer": ["정적 타이핑 언어"],
                }
            ],
            score=10,
            correct_answer_count=1,
            started_at="2025-02-01T11:20:00Z",
        )

        cls.list_url = reverse("exam-submission-admin-list")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def _get_detail_url(self, submission_id: int) -> str:
        return reverse("exam-submission-admin-detail", kwargs={"submission_id": submission_id})

    def test_get_submission_list_success(self) -> None:
        """쪽지시험 응시 내역 목록 조회 성공 테스트 (GET)"""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("next", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 1)

        result = response.data["results"][0]
        self.assertEqual(result["submission_id"], self.submission.pk)
        self.assertEqual(result["nickname"], self.student_user.nickname)
        self.assertEqual(result["name"], self.student_user.name)
        self.assertEqual(result["score"], self.submission.score)

    def test_get_submission_list_search_keyword(self) -> None:
        """쪽지시험 응시 내역 목록 조회 - search_keyword 필터 테스트"""
        response = self.client.get(self.list_url, {"search_keyword": "홍길동"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(self.list_url, {"search_keyword": "존재하지않는이름"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_get_submission_list_cohort_filter(self) -> None:
        """쪽지시험 응시 내역 목록 조회 - cohort_id 필터 테스트"""
        response = self.client.get(self.list_url, {"cohort_id": self.cohort.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(self.list_url, {"cohort_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_get_submission_list_exam_filter(self) -> None:
        """쪽지시험 응시 내역 목록 조회 - exam_id 필터 테스트"""
        response = self.client.get(self.list_url, {"exam_id": self.exam.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(self.list_url, {"exam_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_get_submission_list_sort_and_order(self) -> None:
        """쪽지시험 응시 내역 목록 조회 - 정렬 테스트"""
        ExamSubmission.objects.create(
            submitter=self.student_user,
            deployment=self.deployment,
            cheating_count=0,
            answers_json=[],
            score=5,
            correct_answer_count=0,
            started_at="2025-03-01T10:00:00Z",
        )

        response = self.client.get(self.list_url, {"sort": "score", "order": "desc"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(
            response.data["results"][0]["score"],
            response.data["results"][1]["score"],
        )

        response = self.client.get(self.list_url, {"sort": "score", "order": "asc"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(
            response.data["results"][0]["score"],
            response.data["results"][1]["score"],
        )

    def test_get_submission_list_unauthorized_denied(self) -> None:
        """쪽지시험 응시 내역 목록 조회 401 에러코드 테스트"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_get_submission_list_permission_denied(self) -> None:
        """쪽지시험 응시 내역 목록 조회 403 에러코드 테스트"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.student_user))
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "쪽지시험 응시 내역 조회 권한이 없습니다.")

    def test_get_submission_detail_success(self) -> None:
        """쪽지시험 응시 내역 상세 조회 성공 테스트 (GET)"""
        url = self._get_detail_url(self.submission.pk)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("exam", response.data)
        self.assertIn("student", response.data)
        self.assertIn("result", response.data)
        self.assertIn("questions", response.data)

        self.assertEqual(response.data["student"]["name"], self.student_user.name)
        self.assertEqual(response.data["student"]["nickname"], self.student_user.nickname)
        self.assertEqual(response.data["result"]["score"], self.submission.score)
        self.assertEqual(response.data["result"]["correct_answer_count"], self.submission.correct_answer_count)

    def test_get_submission_detail_unauthorized_denied(self) -> None:
        """쪽지시험 응시 내역 상세 조회 401 에러코드 테스트"""
        url = self._get_detail_url(self.submission.pk)
        self.client.force_authenticate(user=None)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_get_submission_detail_permission_denied(self) -> None:
        """쪽지시험 응시 내역 상세 조회 403 에러코드 테스트"""
        url = self._get_detail_url(self.submission.pk)
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.student_user))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "쪽지시험 응시 상세 조회 권한이 없습니다.")

    def test_get_submission_detail_not_found(self) -> None:
        """쪽지시험 응시 내역 상세 조회 404 에러코드 테스트"""
        url = self._get_detail_url(99999)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "해당 응시 내역을 찾을 수 없습니다.")

    def test_delete_submission_success(self) -> None:
        """쪽지시험 응시 내역 삭제 성공 테스트 (DELETE)"""
        submission = ExamSubmission.objects.create(
            submitter=self.student_user,
            deployment=self.deployment,
            cheating_count=0,
            answers_json=[],
            score=0,
            correct_answer_count=0,
            started_at="2025-02-01T11:20:00Z",
        )
        url = self._get_detail_url(submission.pk)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["submission_id"], submission.pk)
        self.assertFalse(ExamSubmission.objects.filter(pk=submission.pk).exists())

    def test_delete_submission_unauthorized_denied(self) -> None:
        """쪽지시험 응시 내역 삭제 401 에러코드 테스트"""
        url = self._get_detail_url(self.submission.pk)
        self.client.force_authenticate(user=None)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_delete_submission_permission_denied(self) -> None:
        """쪽지시험 응시 내역 삭제 403 에러코드 테스트"""
        url = self._get_detail_url(self.submission.pk)
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.student_user))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "쪽지시험 응시 내역 삭제 권한이 없습니다.")

    def test_delete_submission_not_found(self) -> None:
        """쪽지시험 응시 내역 삭제 404 에러코드 테스트"""
        url = self._get_detail_url(99999)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "삭제할 응시 내역을 찾을 수 없습니다.")
