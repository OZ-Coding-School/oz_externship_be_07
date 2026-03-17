from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import Answers, QuestionCategories, Questions
from apps.users.models.models import User


class AnswerAcceptTest(TestCase):
    user: User
    other_user: User
    category: QuestionCategories
    question: Questions
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="accept@example.com",
            nickname="질문자",
            name="채택유저",
            phone_number="010-0001-0004",
            gender="MALE",
            birthday=date(1990, 1, 1),
        )
        cls.other_user = User.objects.create_user(
            email="accept_other@example.com",
            nickname="답변자",
            name="타인유저",
            phone_number="010-0001-0005",
            gender="FEMALE",
            birthday=date(1990, 1, 1),
        )
        cls.category = QuestionCategories.objects.create(name="채택테스트")
        cls.question = Questions.objects.create(
            author=cls.user, category=cls.category, title="채택 질문", content="질문내용"
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # 미인증 → 401
    def test_accept_answer_unauthenticated(self) -> None:
        answer = Answers.objects.create(author=self.other_user, questions=self.question, content="답변")
        self.client.force_authenticate(user=None)
        response = self.client.post(f"/api/v1/qna/answers/{answer.id}/accept")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 질문자 아닌 사람이 채택 → 403 + error_detail 확인
    def test_accept_answer_forbidden(self) -> None:
        answer = Answers.objects.create(author=self.other_user, questions=self.question, content="채택 대기 답변")
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(f"/api/v1/qna/answers/{answer.id}/accept")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "본인이 작성한 질문의 답변만 채택할 수 있습니다.")

    # 이미 채택된 답변 존재 → 409 + error_detail 확인
    def test_accept_answer_conflict(self) -> None:
        Answers.objects.create(
            author=self.other_user, questions=self.question, content="이미 채택된 답변", is_adopted=True
        )
        new_answer = Answers.objects.create(author=self.other_user, questions=self.question, content="새 답변")
        response = self.client.post(f"/api/v1/qna/answers/{new_answer.id}/accept")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("error_detail", response.data)

    # 존재하지 않는 답변 → 404
    def test_accept_answer_not_found(self) -> None:
        response = self.client.post("/api/v1/qna/answers/99999/accept")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
