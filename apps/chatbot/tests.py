import json
import uuid
from typing import Any, cast
from unittest.mock import MagicMock, patch

from django.core.cache import caches
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.chatbot.choices import BotTypeChoices, MessageRoleChoices
from apps.users.models.models import User

from .serializers import ChatbotCompletionRequestSerializer

chatbot_cache = caches["chatbot"]


class ChatbotSerializerTest(TestCase):
    """
    [stateless] 시리얼라이저 유효성 테스트
    """

    # def test_completion_request_serializer_valid(self) -> None:
    #     """입력값 검증 시리얼라이저"""
    #     valid_data = {
    #         "message": "테스트 질문입니다.",
    #         "bot_type": "support",
    #     }
    #     serializer = ChatbotCompletionRequestSerializer(data=valid_data)
    #     self.assertTrue(serializer.is_valid())
    #     self.assertEqual(serializer.validated_data["bot_type"], BotTypeChoices.SUPPORT.value)

    # def test_completion_request_serializer_default_bot_type(self) -> None:
    #     """bot_type 아닐 때 기본값 qna 홗인"""
    #     valid_data = {"message": "테스트 질문입니다."}
    #     serializer = ChatbotCompletionRequestSerializer(data=valid_data)
    #     self.assertTrue(serializer.is_valid())
    #     self.assertEqual(serializer.validated_data["bot_type"], BotTypeChoices.QNA.value)

    # def tearDown(self) -> None:
    #     caches["chatbot"].clear()


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
