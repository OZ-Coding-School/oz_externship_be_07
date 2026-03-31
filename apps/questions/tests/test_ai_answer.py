from datetime import date
from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import QuestionCategories, Questions
from apps.users.models.models import User


def make_mock_gemini() -> MagicMock:
    mock_instance = MagicMock()
    mock_instance.models.generate_content.return_value = MagicMock(text="AI 답변 내용")
    return mock_instance


class AIAnswerTest(TestCase):
    user: User
    category: QuestionCategories
    question: Questions
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="ai@example.com",
            nickname="AI테스터",
            name="AI유저",
            phone_number="010-0001-0008",
            gender="MALE",
            birthday=date(1998, 8, 8),
        )
        cls.category = QuestionCategories.objects.create(name="AI테스트")
        cls.question = Questions.objects.create(
            author=cls.user, category=cls.category, title="AI 질문", content="AI 답변 요청"
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # 미인증 → 401
    def test_ai_answer_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response = self.client.get(f"/api/v1/qna/questions/{self.question.id}/ai-answer")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 존재하지 않는 질문 → 404
    def test_ai_answer_question_not_found(self) -> None:
        response = self.client.get("/api/v1/qna/questions/99999/ai-answer")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 중복 생성 → 기존 데이터 반환 확인
    def test_ai_answer_conflict(self) -> None:
        url = f"/api/v1/qna/questions/{self.question.id}/ai-answer"
        with patch("apps.questions.services.answers_services.genai.Client", return_value=make_mock_gemini()):
            self.client.get(url)
            response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("output", response.data)
        self.assertIn("id", response.data)
