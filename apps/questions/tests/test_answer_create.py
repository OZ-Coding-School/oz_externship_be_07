from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import AnswerImages, QuestionCategories, Questions
from apps.users.models.models import User


class AnswerCreateTest(TestCase):
    user: User
    category: QuestionCategories
    question: Questions
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="create@example.com",
            nickname="등록자",
            name="등록유저",
            phone_number="010-0001-0001",
            gender="MALE",
            birthday=date(2000, 1, 1),
        )
        cls.category = QuestionCategories.objects.create(name="등록테스트")
        cls.question = Questions.objects.create(
            author=cls.user, category=cls.category, title="테스트 질문", content="질문내용"
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # 미인증 → 401
    def test_create_answer_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response = self.client.post(
            f"/api/v1/qna/questions/{self.question.id}/answers",
            {"content": "테스트"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 내용 없음 → 400
    def test_create_answer_missing_content(self) -> None:
        response = self.client.post(
            f"/api/v1/qna/questions/{self.question.id}/answers",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 존재하지 않는 질문 → 404
    def test_create_answer_question_not_found(self) -> None:
        response = self.client.post(
            "/api/v1/qna/questions/99999/answers",
            {"content": "테스트"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 이미지 포함 등록 → 이미지 DB 저장 확인
    def test_create_answer_with_image(self) -> None:
        response = self.client.post(
            f"/api/v1/qna/questions/{self.question.id}/answers",
            {"content": "이미지 포함 답변", "image_urls": ["https://cdn.example.com/test.png"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            AnswerImages.objects.filter(
                answer_id=response.data["answer_id"],
                img_url="https://cdn.example.com/test.png",
            ).exists()
        )
