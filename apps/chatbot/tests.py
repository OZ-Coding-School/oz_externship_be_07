import uuid
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

from apps.chatbot.choices import ChatbotModelChoices
from apps.chatbot.models import ChatbotCompletions, ChatbotSessions
from apps.chatbot.tasks import delete_expired_chatbot_sessions
from apps.questions.models import QuestionCategories, Questions
from apps.users.models.models import User

chatbot_cache = caches["chatbot"]


class ChatbotIntegrationTest(APITestCase):
    def setUp(self) -> None:
        # 테스트 유저 생성 및 ADMIN 권한 부여
        self.user = User.objects.create_user(
            email="test@test.com",
            password="password123!",
            nickname="테스터",
            name="홍길동",
            birthday="1995-01-01",
            role="ADMIN",
        )
        self.client.force_authenticate(user=self.user)

        # 테스트용 카테고리
        self.category = QuestionCategories.objects.create(name="테스트 카테고리")

        # 테스트용 질문글 생성
        self.question = Questions.objects.create(
            author=self.user,
            title="테스트 질문",
            content="테스트 내용",
            category=self.category,
        )

        # 테스트용 세션 생성
        self.session = ChatbotSessions.objects.create(
            user=self.user,
            question=self.question,
            title="기존 세션",
            using_model=ChatbotModelChoices.GEMINI_2_0_FLASH_LITE_001.value,
        )

    def test_session_list_create_flow(self) -> None:
        """세션 목록 조회 및 생성 로직 커버"""
        # <GET> 목록 조회 (views)
        url = reverse("chatbot:session-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # <POST> 새 세션 생성 (views post, service의 create 커버)
        new_question = Questions.objects.create(
            author=self.user, category=self.category, title="새로운 테스트 질문", content="내용"
        )
        data = {"question_id": new_question.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], ChatbotSessions.objects.latest("id").id)

    def test_session_detail_delete_flow(self) -> None:
        """세션 상세 조회 및 삭제 로직 커버"""
        url = reverse("chatbot:session-detail", kwargs={"session_id": self.session.id})

        # <GET> 상세 조회 (service.get_session_detail_for_user 커버)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # <DELETE> 삭제 (service.delete_session 커버)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ChatbotSessions.objects.filter(id=self.session.id).exists())

    @override_settings(GEMINI_API_KEY="fake_key_for_test")
    @patch("apps.chatbot.services.chatbot_service.genai.Client")
    def test_chatbot_completion_streaming(self, mock_genai: MagicMock) -> None:
        """AI 스트리밍 응답"""
        url = reverse("chatbot:session-completions", kwargs={"session_id": self.session.id})

        mock_response = [MagicMock(text="테스트중"), MagicMock(text="테스트가 안 끝나")]
        mock_genai.return_value.models.generate_content_stream.return_value = mock_response

        data = {"message": "자고싶다."}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        streaming_response = cast(StreamingHttpResponse, response)

        content_iterator = cast(Iterator[bytes], streaming_response.streaming_content)
        full_content = b"".join(content_iterator)

        self.assertIn("테스트".encode("utf-8"), full_content)


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
        caches["chatbot"].clear()


class ChatbotTaskTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="task_test@test.com",
            password="pass",
            nickname="테스터",
            name="홍길동",
            birthday="1995-01-01",
            role="ADMIN",
        )
        self.category = QuestionCategories.objects.create(name="테스트")
        self.question = Questions.objects.create(author=self.user, category=self.category, title="T", content="C")

    def test_delete_expired_sessions_task(self) -> None:
        """만료된 세션 삭제 태스크 로직 커버"""
        expired_session = ChatbotSessions.objects.create(user=self.user, question=self.question, title="오래된 방")
        # auto_now=True 필드는 save() 시점에 현재 시간이 찍히므로,
        # .update() 명령으로 DB 레벨에서 강제로 과거 시간을 주입
        expired_date = timezone.now() - timedelta(hours=2)
        ChatbotSessions.objects.filter(id=expired_session.id).update(updated_at=expired_date)

        question2 = Questions.objects.create(
            author=self.user, category=self.category, title="두 번째 질문", content="내용"
        )

        valid_session = ChatbotSessions.objects.create(user=self.user, question=question2, title="싱싱한 방")

        # 태스크 함수 '직접' 호출
        deleted_count = delete_expired_chatbot_sessions()

        self.assertGreaterEqual(deleted_count, 1)
        self.assertFalse(ChatbotSessions.objects.filter(id=expired_session.id).exists())
        self.assertTrue(ChatbotSessions.objects.filter(id=valid_session.id).exists())
