import json
from typing import Any, cast
from unittest.mock import MagicMock, patch

from django.http import StreamingHttpResponse
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from apps.chatbot.choices import ChatbotModelChoices, MessageRoleChoices
from apps.chatbot.models import ChatbotCompletions, ChatbotSessions
from apps.questions.models import QuestionCategories, Questions
from apps.users.models.models import User

from .serializers import (
    ChatbotSessionCreateSerializer,
    ChatbotSessionReadSerializer,
)


class ChatbotSerializerTest(TestCase):
    user: User
    category: QuestionCategories
    question: Questions

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="ser_test@test.com",
            password="testpassword123",
            name="태리 테스터",
            nickname="sir_nick",
            phone_number="01011112222",
            gender="MALE",
            birthday="2000-01-01",
        )
        cls.category = QuestionCategories.objects.create()
        cls.question = Questions.objects.create(
            title="테스트 질문",
            content="내용",
            category_id=cls.category.id,
        )

    def test_create_serializer_valid(self) -> None:
        factory = APIRequestFactory()
        request = factory.post("/api/v1/chatbot/sessions")
        request.user = self.user
        valid_data = {
            "question": self.question.id,
            "title": "시리얼라이저 테스트",
            "using_model": ChatbotModelChoices.GEMINI_2_5_FLASH,
        }
        serializer = ChatbotSessionCreateSerializer(data=valid_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        session = serializer.save()
        self.assertEqual(session.user, self.user)


class ChatbotViewTest(APITestCase):
    user: User
    category: QuestionCategories
    question: Questions
    session: ChatbotSessions
    completion_url = str

    def setUp(self) -> None:
        self.user, _ = User.objects.get_or_create(
            email="view_test@test.com",
            defaults={
                "name": "뷰테스터",
                "nickname": "view_nick",
                "phone_number": "01099998888",
                "gender": "FEMALE",
                "birthday": "1995-05-05",
            },
        )
        if not self.user.has_usable_password():
            self.user.set_password("testpassword123")
            self.user.save()

        self.client.force_authenticate(user=self.user)
        self.category = QuestionCategories.objects.create()
        self.question = Questions.objects.create(title="질문", content="내용", category_id=self.category.id)
        self.session = ChatbotSessions.objects.create(
            user=self.user,
            question=self.question,
            title="테스트 세션",
            using_model=ChatbotModelChoices.GEMINI_2_5_FLASH,
        )

    def test_get_completions(self) -> None:
        """대화 내역 조회 GET"""
        ChatbotCompletions.objects.create(session=self.session, role=MessageRoleChoices.USER, message="안녕")
        url = reverse("chatbot:session-completions", kwargs={"session_id": self.session.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_completions(self) -> None:
        """대화 내역 초기화 DELETE"""
        url = reverse("chatbot:session-completions", kwargs={"session_id": self.session.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.chatbot.services.chatbot_service.genai.Client")
    def test_post_completion_streaming_success(self, mock_client_class: MagicMock) -> None:
        """AI 스트리밍 답변 생성 POST (201 Created 및 DB 저장 확인)"""

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_chunk = MagicMock()
        mock_chunk.text = "답변이 생성되지 않아 DB에 저장되지 않았는데 "
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "DB에 저장된 유저질문이 1개였음."

        mock_client.models.generate_content_stream.return_value = [mock_chunk, mock_chunk2]

        url = reverse("chatbot:session-completions", kwargs={"session_id": self.session.id})
        data = {"message": "테스트 메시지"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        streaming_content = b"".join(cast(Any, response).streaming_content).decode()
        self.assertIn("답변이 생성되지 않아 DB에 저장되지 않았는데 ", streaming_content)
        self.assertIn("DB에 저장된 유저질문이 1개였음.", streaming_content)

        self.assertIn("[DONE]", streaming_content)

        self.assertEqual(ChatbotCompletions.objects.filter(session=self.session).count(), 2)

    def test_session_list_get(self) -> None:
        """세션 목록 조회"""
        url = reverse("chatbot:session-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_session_delete(self) -> None:
        """세션 삭제"""
        url = reverse("chatbot:session-detail", kwargs={"session_id": self.session.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_support_session_create(self) -> None:
        """고객지원 세션 생성"""
        url = reverse("chatbot:session-support-create")
        data = {"title": "지원 세션", "question": self.question.id, "using_model": ChatbotModelChoices.GEMINI_2_5_FLASH}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
