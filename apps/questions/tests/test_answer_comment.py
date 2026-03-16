from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import AnswerComments, Answers, QuestionCategories, Questions
from apps.users.models.models import User


class AnswerCommentTest(TestCase):
    user: User
    other_user: User
    category: QuestionCategories
    question: Questions
    answer: Answers
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="comment@example.com",
            nickname="댓글러",
            name="댓글유저",
            phone_number="010-0001-0006",
            gender="MALE",
            birthday=date(1993, 6, 6),
        )
        cls.other_user = User.objects.create_user(
            email="comment_other@example.com",
            nickname="답변자2",
            name="답변유저",
            phone_number="010-0001-0007",
            gender="FEMALE",
            birthday=date(1993, 6, 6),
        )
        cls.category = QuestionCategories.objects.create(name="댓글테스트")
        cls.question = Questions.objects.create(
            author=cls.user, category=cls.category, title="댓글 질문", content="질문내용"
        )
        cls.answer = Answers.objects.create(author=cls.other_user, questions=cls.question, content="답변내용")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # 미인증 → 401
    def test_create_comment_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response = self.client.post(
            f"/api/v1/qna/answers/{self.answer.id}/comments",
            {"content": "댓글"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 내용 없음 → 400
    def test_create_comment_empty_content(self) -> None:
        response = self.client.post(
            f"/api/v1/qna/answers/{self.answer.id}/comments",
            {"content": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 500자 초과 → 400
    def test_create_comment_too_long(self) -> None:
        response = self.client.post(
            f"/api/v1/qna/answers/{self.answer.id}/comments",
            {"content": "가" * 501},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 존재하지 않는 답변 → 404
    def test_create_comment_answer_not_found(self) -> None:
        response = self.client.post(
            "/api/v1/qna/answers/99999/comments",
            {"content": "댓글"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 댓글 등록 후 DB 저장 확인
    def test_create_comment_saved_to_db(self) -> None:
        response = self.client.post(
            f"/api/v1/qna/answers/{self.answer.id}/comments",
            {"content": "좋은 답변이네요!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AnswerComments.objects.filter(id=response.data["comment_id"]).exists())
