import json
from datetime import timedelta
from typing import Any, Iterator, cast
from unittest.mock import MagicMock, patch

from django.core.cache import caches
from django.http import StreamingHttpResponse
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.chatbot.choices import ChatbotModelChoices, MessageRoleChoices
from apps.chatbot.models import ChatbotCompletions, ChatbotSessions
from apps.chatbot.tasks import delete_expired_chatbot_sessions
from apps.questions.models import QuestionCategories, Questions
from apps.users.models.models import User


class ChatbotSessionTest(APITestCase):
    """QnA 챗봇 세션 CRUD 테스트"""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@test.com",
            password="password123!",
            nickname="테스터",
            name="홍길동",
            birthday="1995-01-01",
        )
        self.client.force_authenticate(user=self.user)

        self.category = QuestionCategories.objects.create(name="테스트 카테고리")
        self.question = Questions.objects.create(
            author=self.user,
            title="테스트 질문",
            content="테스트 내용",
            category=self.category,
        )
        self.session = ChatbotSessions.objects.create(
            user=self.user,
            question=self.question,
            title="기존 세션",
            using_model=ChatbotModelChoices.GEMINI_2_5_FLASH_LITE.value,
        )

    def test_session_list(self) -> None:
        """세션 목록 커서 페이지네이션 조회"""
        url = reverse("chatbot:session-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["results"][0]["user"], self.user.id)
        self.assertEqual(response.data["results"][0]["question_id"], self.question.id)

    def test_session_create(self) -> None:
        """세션 생성"""
        new_question = Questions.objects.create(
            author=self.user, category=self.category, title="새 질문", content="내용"
        )
        url = reverse("chatbot:session-list-create")
        response = self.client.post(url, {"question_id": new_question.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["question_id"], new_question.id)
        self.assertEqual(response.data["user"], self.user.id)

    def test_session_create_existing(self) -> None:
        """이미 존재하는 세션이면 200 반환"""
        url = reverse("chatbot:session-list-create")
        response = self.client.post(url, {"question_id": self.question.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_session_create_question_not_found(self) -> None:
        """없는 질문으로 세션 생성 시 404"""
        url = reverse("chatbot:session-list-create")
        response = self.client.post(url, {"question_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_session_delete(self) -> None:
        """세션 삭제"""
        url = reverse("chatbot:session-detail", kwargs={"session_id": self.session.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ChatbotSessions.objects.filter(id=self.session.id).exists())

    def test_session_delete_not_found(self) -> None:
        """없는 세션 삭제 시 404"""
        url = reverse("chatbot:session-detail", kwargs={"session_id": 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ChatbotCompletionTest(APITestCase):
    """QnA 챗봇 대화 관련 테스트"""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="comp@test.com",
            password="password123!",
            nickname="컴테",
            name="김테스트",
            birthday="1995-01-01",
        )
        self.client.force_authenticate(user=self.user)

        self.category = QuestionCategories.objects.create(name="카테고리")
        self.question = Questions.objects.create(author=self.user, title="질문", content="내용", category=self.category)
        self.session = ChatbotSessions.objects.create(
            user=self.user,
            question=self.question,
            title="세션",
            using_model=ChatbotModelChoices.GEMINI_2_5_FLASH_LITE.value,
        )

    def test_completion_list(self) -> None:
        """대화내역 조회 커서 페이지네이션"""
        ChatbotCompletions.objects.create(session=self.session, message="안녕", role=MessageRoleChoices.USER)
        url = reverse("chatbot:session-completions", kwargs={"session_id": self.session.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    @override_settings(GEMINI_API_KEY="fake_key")
    @patch("apps.chatbot.services.chatbot_service.genai.Client")
    def test_completion_streaming_sse_format(self, mock_genai: MagicMock) -> None:
        """SSE 포맷 스트리밍 응답 확인"""
        mock_response = [MagicMock(text="테스트"), MagicMock(text="응답")]
        mock_genai.return_value.models.generate_content_stream.return_value = mock_response

        url = reverse("chatbot:session-completions", kwargs={"session_id": self.session.id})
        response = self.client.post(url, {"message": "질문입니다"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        streaming_response = cast(StreamingHttpResponse, response)
        content_iterator = cast(Iterator[bytes], streaming_response.streaming_content)
        chunks = [chunk.decode("utf-8") for chunk in content_iterator]

        # SSE 포맷 검증
        self.assertTrue(chunks[0].startswith("data: "))
        parsed = json.loads(chunks[0].replace("data: ", "").strip())
        self.assertIn("content", parsed)
        self.assertEqual(chunks[-1].strip(), "data: [DONE]")

    @override_settings(GEMINI_API_KEY="fake_key")
    @patch("apps.chatbot.services.chatbot_service.genai.Client")
    def test_completion_limit_exceeded(self, mock_genai: MagicMock) -> None:
        """질문 횟수 초과 시 429"""
        for i in range(3):
            ChatbotCompletions.objects.create(session=self.session, message=f"질문 {i}", role=MessageRoleChoices.USER)

        url = reverse("chatbot:session-completions", kwargs={"session_id": self.session.id})
        response = self.client.post(url, {"message": "4번째 질문"})
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("질문 게시판", response.data["error_detail"])

    def test_completion_session_not_found(self) -> None:
        """없는 세션으로 대화 시도 시 404"""
        url = reverse("chatbot:session-completions", kwargs={"session_id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ChatbotSupportTest(APITestCase):
    """CS 상담 챗봇 테스트"""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="support@test.com",
            password="password123!",
            nickname="상담",
            name="이상담",
            birthday="1995-01-01",
        )
        self.client.force_authenticate(user=self.user)

    @override_settings(GEMINI_API_KEY="fake_key")
    @patch("apps.chatbot.services.chatbot_service.genai.Client")
    def test_support_streaming(self, mock_genai: MagicMock) -> None:
        """CS 상담 SSE 스트리밍"""
        mock_response = [MagicMock(text="안녕하세요")]
        mock_genai.return_value.models.generate_content_stream.return_value = mock_response

        url = reverse("chatbot:support")
        response = self.client.post(url, {"message": "수강 문의"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        streaming_response = cast(StreamingHttpResponse, response)
        content_iterator = cast(Iterator[bytes], streaming_response.streaming_content)
        chunks = [chunk.decode("utf-8") for chunk in content_iterator]
        self.assertTrue(chunks[0].startswith("data: "))

    def test_support_empty_message(self) -> None:
        """빈 메시지 시 400"""
        url = reverse("chatbot:support")
        response = self.client.post(url, {"message": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChatbotTaskTest(APITestCase):
    """Celery 만료 세션 삭제 태스크 테스트"""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="task@test.com",
            password="pass",
            nickname="태스크",
            name="홍길동",
            birthday="1995-01-01",
        )
        self.category = QuestionCategories.objects.create(name="테스트")
        self.question = Questions.objects.create(author=self.user, category=self.category, title="T", content="C")

    def test_delete_expired_sessions(self) -> None:
        """만료된 세션 삭제, 유효 세션 유지"""
        expired = ChatbotSessions.objects.create(user=self.user, question=self.question, title="만료")
        ChatbotSessions.objects.filter(id=expired.id).update(updated_at=timezone.now() - timedelta(hours=2))

        q2 = Questions.objects.create(author=self.user, category=self.category, title="Q2", content="C")
        valid = ChatbotSessions.objects.create(user=self.user, question=q2, title="유효")

        deleted_count = delete_expired_chatbot_sessions()

        self.assertGreaterEqual(deleted_count, 1)
        self.assertFalse(ChatbotSessions.objects.filter(id=expired.id).exists())
        self.assertTrue(ChatbotSessions.objects.filter(id=valid.id).exists())
