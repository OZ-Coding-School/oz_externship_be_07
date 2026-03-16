from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import Answers, QuestionCategories, Questions
from apps.users.models.models import User


class AnswerUpdateTest(TestCase):
    user: User
    other_user: User
    category: QuestionCategories
    question: Questions
    answer: Answers
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="update@example.com",
            nickname="수정자",
            name="수정유저",
            phone_number="010-0001-0002",
            gender="MALE",
            birthday=date(1995, 3, 3),
        )
        cls.other_user = User.objects.create_user(
            email="update_other@example.com",
            nickname="타인",
            name="타인유저",
            phone_number="010-0001-0003",
            gender="FEMALE",
            birthday=date(1995, 3, 3),
        )
        cls.category = QuestionCategories.objects.create(name="수정테스트")
        cls.question = Questions.objects.create(
            author=cls.user, category=cls.category, title="수정 질문", content="질문내용"
        )
        cls.answer = Answers.objects.create(author=cls.user, questions=cls.question, content="원본 답변")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # 미인증 → 401
    def test_update_answer_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response = self.client.put(
            f"/api/v1/qna/answers/{self.answer.id}",
            {"content": "수정"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 내용 없음 → 400
    def test_update_answer_missing_content(self) -> None:
        response = self.client.put(
            f"/api/v1/qna/answers/{self.answer.id}",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 타인 수정 → 403 + error_detail 확인
    def test_update_answer_forbidden(self) -> None:
        self.client.force_authenticate(user=self.other_user)
        response = self.client.put(
            f"/api/v1/qna/answers/{self.answer.id}",
            {"content": "무단수정"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "본인이 작성한 답변만 수정할 수 있습니다.")

    # 존재하지 않는 답변 → 404
    def test_update_answer_not_found(self) -> None:
        response = self.client.put(
            "/api/v1/qna/answers/99999",
            {"content": "없는답변"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
