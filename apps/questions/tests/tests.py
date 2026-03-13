from datetime import date
from unicodedata import category
from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import AnswerImages, Answers, QuestionCategories, Questions
from apps.users.models.models import User


class AnswerAPITest(TestCase):
    # 클래스 레벨 타입 어노테이션 (그냥 할당X) -> 필드 인식
    user: User
    other_user: User
    category: QuestionCategories
    question: Questions
    client: APIClient

    @classmethod
    def setUpTestData(cls) -> None:  # setUpTestData(cls) 사용
        cls.user = User.objects.create_user(
            email="test_dev@example.com",
            nickname="테스트",
            name="이규빈",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday=date(2000, 1, 1),
        )
        cls.other_user = User.objects.create_user(
            email="other_dev@example.com",
            nickname="타인이준님",
            name="이주운코우치",
            phone_number="010-1234-4321",
            gender="FEMALE",
            birthday=date(1950, 5, 5),
        )

        cls.category = QuestionCategories.objects.create(name="테스트카테고리")
        cls.question = Questions.objects.create(
            author=cls.user, category=cls.category, title="장고 테스트 질문", content="setUpTestData를 써봅시다.."
        )

    def setUp(self) -> None:
        # 테스트마다 달라져야 하는 (클라이언트, 토큰)만 setUp에 남김 -> 테스트 속도 향상
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # 답변 등록 / 이미지 첨부 테스트
    def test_create_answer_success(self) -> None:
        url = f"/api/v1/qna/questions/{self.question.id}/answers"
        data = {"content": "속도 향상을 위해...", "image_urls": ["https://cdn.example.com/test.png"]}  # 명세서 필드명
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_answer = Answers.objects.get(id=response.data["answer_id"])  # id 하드코딩 금지,,
        self.assertEqual(created_answer.author, self.user)
        # 실제 이미지 데이터가 생성되었는지도 함께 확인
        self.assertTrue(AnswerImages.objects.filter(img_url="https://cdn.example.com/test.png").exists())

    # AI 답변 생성 테스트
    def test_generate_ai_answer_success(self) -> None:
        url = f"/api/v1/qna/questions/{self.question.id}/ai-answer"

        # 실제 Gemini API 호출 대신 mock으로 대체
        with patch("apps.questions.services.answers_services.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value.text = "AI 답변 내용"
            mock_genai.GenerativeModel.return_value = mock_model

            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["using_model"], "gemini-2.5-pro")
        self.assertIn("id", response.data)

    # 답변 채택 권한 테스트
    def test_accept_answer_forbidden(self) -> None:  # 타인이 작성한 답변 생성
        answer = Answers.objects.create(
            author=self.other_user, questions=self.question, content="채택되길 기다리는 답변"
        )

        # 질문자가 아닌 'other_user'로 채택 시도
        self.client.force_authenticate(user=self.other_user)
        url = f"/api/v1/qna/answers/{answer.id}/accept"
        response = self.client.post(url)

        # 권한이 없다면 403에러 확인
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "본인이 작성한 질문의 답변만 채택할 수 있습니다.")

    # 댓글 글자수 테스트
    def test_create_comment_length_limit(self) -> None:
        answer = Answers.objects.create(author=self.other_user, questions=self.question, content="답변")
        url = f"/api/v1/qna/answers/{answer.id}/comments"

        # 500자 초과 데이터 생성해보기
        long_content = "가" * 501
        response = self.client.post(url, {"content": long_content})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "댓글 내용은 1~500자 사이로 입력해야 합니다.")
