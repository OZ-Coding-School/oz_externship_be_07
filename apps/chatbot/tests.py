import json
import uuid
from typing import Any, cast
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.chatbot.choices import MessageRoleChoices
from apps.users.models.models import User

from .serializers import ChatbotCompletionRequestSerializer


class ChatbotSerializerTest(TestCase):
    """
    [stateless] 시리얼라이저 유효성 테스트
    """

    def test_completion_request_serializer_valid(self) -> None:
        """입력값 검증 시리얼라이저"""
        valid_data = {
            "message": "테스트 질문입니다.",
            "bot_type": "support",
        }
        serializer = ChatbotCompletionRequestSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["bot_type"], "support")

    def test_completion_request_serializer_default_bot_type(self) -> None:
        """bot_type 아닐 때 기본값 qna 홗인"""
        valid_data = {"message": "테스트 질문입니다."}
        serializer = ChatbotCompletionRequestSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["bot_type"], "qna")


class ChatbotStatelessViewTest(APITestCase):
    """Redis 기반 챗봇 스트리밍 및 세션 뷰 테스트"""

    def setUp(self) -> None:
        # 유저 생성, 로그인
        self.user = User.objects.create_user(
            email="ser_test@test.com",
            password="testpassword123",
            name="태리 테스터",
            nickname="sir_nick",
            phone_number="01011112222",
            gender="MALE",
            birthday="2000-01-01",
        )
        self.client.force_authenticate(user=self.user)

        # 임시 세션 ID (UUID) 발급, 캐시 최ㄱ화
        self.session_id = str(uuid.uuid4())
        cache.clear()

    def test_create_ephemeral_session(self) -> None:
        """[방생성] DB없이 UUID 세션 ID만 발급하는지 확인"""
        url = reverse("chatbot:session-create")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("session_id", response.data)
        self.assertIsInstance(response.data["session_id"], str)

    def test_get_complerions_empty(self) -> None:
        """[내역 조회] 빈 대화 내역 조회시"""
        url = reverse("chatbot:chatbot-completions", kwargs={"bot_type": "qna", "session_id": self.session_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_ephemeral_completions(self) -> None:
        """[내역 삭제] Redis 캐시 초기화 확인"""
        history_key = f"chatbot:qna:history{self.session_id}"
        cache.set(history_key, [{"role": "user", "message": "되다."}], timeout=3600)

        url = reverse("chatbot:chatbot-completions", kwargs={"bot_type": "qna", "session_id": self.session_id})
        response = self.client.delete(url)

    @override_settings(GEMINI_API_KEY="dummy_test_key_for_CI")
    @patch("apps.chatbot.services.chatbot_service.genai.Client")
    def test_post_completion_streaming_success(self, mock_client_class: MagicMock) -> None:
        """[AI응답] 스트리밍 성공 및 Redis 캐시 저장 확인"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_chunk = MagicMock()
        mock_chunk.text = "안녕하세요.김이준입니다. "
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "근육짱짱맨"
        mock_client.models.generate_content_stream.return_value = [mock_chunk, mock_chunk2]

        url = reverse("chatbot:chatbot-completions", kwargs={"bot_type": "qna", "session_id": self.session_id})
        data = {"message": "테스트로 텍스트"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        streaming_content = b"".join(cast(Any, response).streaming_content).decode("utf-8")
        self.assertIn("안녕하세요.김이준입니다. ", streaming_content)
        self.assertIn("근육짱짱맨", streaming_content)
        self.assertIn("[DONE]", streaming_content)

        history = cache.get(f"chatbot:qna:history:{self.session_id}")
        self.assertIsNotNone(history)
        self.assertEqual(len(history), 2)  # 유저질문 1개, AI 1개 = 총 2개
        self.assertEqual(history[0]["role"], MessageRoleChoices.USER)
        self.assertEqual(history[1]["role"], MessageRoleChoices.ASSISTANT)

    def test_qna_bot_limit_exceeded(self) -> None:
        """[횟수 제한] QnA 챗봇 2회 질문 초과 시 403 에러 반환"""
        count_key = f"chatbot:count:{self.session_id}"
        cache.set(count_key, 2)

        url = reverse("chatbot:chatbot-completions", kwargs={"bot_type": "qna", "session_id": self.session_id})
        data = {"message": "더 궁금하진 점은 질문 게시판을 이용하시기 바랍니다."}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
