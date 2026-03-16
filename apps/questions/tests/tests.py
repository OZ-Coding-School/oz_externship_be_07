from datetime import date
from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.questions.models import AnswerComments, AnswerImages, Answers, QuestionCategories, Questions
from apps.users.models.models import User


def make_mock_gemini() -> MagicMock:
    mock_instance = MagicMock()
    mock_instance.models.generate_content.return_value = MagicMock(text="AI 답변 내용")
    return mock_instance


class AnswerCreateTest(TestCase):
    user: User
    category: QuestionCategories
    question: Questions

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


class AnswerUpdateTest(TestCase):
    user: User
    other_user: User
    category: QuestionCategories
    question: Questions
    answer: Answers

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
        cls.answer = Answers.objects.create(
            author=cls.user, questions=cls.question, content="원본 답변"
        )

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

    # 내용 없음 → 400
    def test_update_answer_missing_content(self) -> None:
        response = self.client.put(
            f"/api/v1/qna/answers/{self.answer.id}",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AnswerAcceptTest(TestCase):
    user: User
    other_user: User
    category: QuestionCategories
    question: Questions

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
        answer = Answers.objects.create(
            author=self.other_user, questions=self.question, content="답변"
        )
        self.client.force_authenticate(user=None)
        response = self.client.post(f"/api/v1/qna/answers/{answer.id}/accept")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 질문자 아닌 사람이 채택 → 403 + error_detail 확인
    def test_accept_answer_forbidden(self) -> None:
        answer = Answers.objects.create(
            author=self.other_user, questions=self.question, content="채택 대기 답변"
        )
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
        new_answer = Answers.objects.create(
            author=self.other_user, questions=self.question, content="새 답변"
        )
        response = self.client.post(f"/api/v1/qna/answers/{new_answer.id}/accept")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("error_detail", response.data)

    # 존재하지 않는 답변 → 404
    def test_accept_answer_not_found(self) -> None:
        response = self.client.post("/api/v1/qna/answers/99999/accept")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AnswerCommentTest(TestCase):
    user: User
    other_user: User
    category: QuestionCategories
    question: Questions
    answer: Answers

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
        cls.answer = Answers.objects.create(
            author=cls.other_user, questions=cls.question, content="답변내용"
        )

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
        self.assertTrue(
            AnswerComments.objects.filter(id=response.data["comment_id"]).exists()
        )


class AIAnswerTest(TestCase):
    user: User
    category: QuestionCategories
    question: Questions

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

    # 중복 생성 → 409 + error_detail 확인
    def test_ai_answer_conflict(self) -> None:
        url = f"/api/v1/qna/questions/{self.question.id}/ai-answer"
        with patch("apps.questions.services.answers_services.genai.Client", return_value=make_mock_gemini()):
            self.client.get(url)
            response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("error_detail", response.data)