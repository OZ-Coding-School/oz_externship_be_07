import json
from typing import Any, Dict, cast

from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.exam.models.choices import QuestionType
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion
from apps.subject.models.choices import SubjectStatus
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject
from apps.users.models.models import User


class ExamQuestionAPITest(APITestCase):
    admin_user: User
    target_user: User
    course: Course
    subject: Subject
    exam: Exam
    question_data: Dict[str, Any]

    @classmethod
    def setUpTestData(cls) -> None:
        """테스트 전체에서 사용할 기본 데이터 설정"""
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

        cls.target_user = user_manager.create(
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

        cls.question_data = {
            "type": QuestionType.SINGLE_CHOICE,
            "question": "다음 중 Python의 특징이 아닌 것은?",
            "prompt": "문제를 잘 읽고 답하세요.",
            "options": ["인터프리터 언어", "동적 타이핑", "플랫폼 독립적", "저급 언어"],
            "blank_count": 0,
            "correct_answer": "저급 언어",
            "point": 10,
            "explanation": "Python은 고급 언어입니다.",
        }

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.admin_user))

    def test_create_question_success(self) -> None:
        """쪽지시험 문제 생성 성공 테스트 (POST)"""
        url = reverse("exam-question-create", kwargs={"exam_id": self.exam.id})
        response = self.client.post(url, self.question_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExamQuestion.objects.filter(exam=self.exam).count(), 1)
        self.assertEqual(response.data["question"], self.question_data["question"])
        self.assertEqual(response.data["correct_answer"], self.question_data["correct_answer"])

    def test_create_question_missing_field_bad_request(self) -> None:
        """필수 필드 누락 시 400 에러 테스트"""
        url = reverse("exam-question-create", kwargs={"exam_id": self.exam.id})
        data = self.question_data.copy()
        data.pop("question")

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_create_question_unauthorized_denied(self) -> None:
        """인증되지 않은 사용자 401 에러 테스트"""
        self.client.force_authenticate(user=None)
        url = reverse("exam-question-create", kwargs={"exam_id": self.exam.id})
        response = self.client.post(url, self.question_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_question_permission_denied(self) -> None:
        """권한 없는 사용자(STUDENT) 403 에러 테스트"""
        self.client.force_authenticate(user=cast(AbstractBaseUser, self.target_user))
        url = reverse("exam-question-create", kwargs={"exam_id": self.exam.id})
        response = self.client.post(url, self.question_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_question_exam_not_found(self) -> None:
        """존재하지 않는 시험에 문제 생성 시 404 에러 테스트"""
        url = reverse("exam-question-create", kwargs={"exam_id": 9999})
        response = self.client.post(url, self.question_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "해당 쪽지시험 정보를 찾을 수 없습니다.")

    def test_create_question_count_conflict(self) -> None:
        """문제 수 초과(10개) 시 409 에러 테스트"""
        for i in range(10):
            ExamQuestion.objects.create(
                exam=self.exam,
                type=QuestionType.SINGLE_CHOICE,
                question=f"question {i}",
                answer="answer",
                point=1,
                explanation="expl",
            )

        url = reverse("exam-question-create", kwargs={"exam_id": self.exam.id})
        response = self.client.post(url, self.question_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["error_detail"], "해당 쪽지시험에 등록 가능한 문제 수 또는 총 배점을 초과했습니다."
        )

    def test_update_question_success(self) -> None:
        """문제 수정 성공 테스트 (PUT)"""
        question = ExamQuestion.objects.create(
            exam=self.exam,
            type=QuestionType.SINGLE_CHOICE,
            question="수정 전 문제",
            answer="수정 전 정답",
            point=5,
            explanation="수정 전 설명",
        )

        url = reverse("exam-question-update-delete", kwargs={"question_id": question.id})
        data = self.question_data.copy()
        data["question"] = "수정 후 문제"

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question"], "수정 후 문제")

        question.refresh_from_db()
        self.assertEqual(question.question, "수정 후 문제")

    def test_update_question_not_found(self) -> None:
        """존재하지 않는 문제 수정 시 404 에러 테스트"""
        url = reverse("exam-question-update-delete", kwargs={"question_id": 9999})
        response = self.client.put(url, self.question_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "수정하려는 문제 정보를 찾을 수 없습니다.")

    def test_delete_question_success(self) -> None:
        """문제 삭제 성공 테스트 (DELETE)"""
        question = ExamQuestion.objects.create(
            exam=self.exam,
            type=QuestionType.SINGLE_CHOICE,
            question="삭제될 문제",
            answer="정답",
            point=5,
            explanation="설명",
        )

        url = reverse("exam-question-update-delete", kwargs={"question_id": question.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question_id"], question.id)
        self.assertFalse(ExamQuestion.objects.filter(id=question.id).exists())

    def test_delete_question_not_found(self) -> None:
        """존재하지 않는 문제 삭제 시 404 에러 테스트"""
        url = reverse("exam-question-update-delete", kwargs={"question_id": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "삭제할 문제 정보를 찾을 수 없습니다.")
