from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework import serializers

from apps.chatbot.models import ChatbotCompletions, ChatbotSessions

if TYPE_CHECKING:
    from django.db.models import Model


class ChatbotCompletionSerializer(serializers.ModelSerializer[ChatbotCompletions]):
    class Meta:
        model = ChatbotCompletions
        fields = ["id", "role", "message", "created_at"]


# 세션 목록 조회
class ChatbotSessionListSerializer(serializers.ModelSerializer[ChatbotSessions]):
    class Meta:
        model = ChatbotSessions
        fields = ["id", "title", "question", "using_model", "created_at", "updated_at"]


# 특정 세션 + 대화 내역 '전체' 조회용
class ChatbotSessionDetailSerializer(serializers.ModelSerializer[ChatbotSessions]):
    # 역참조 (related_name="completions")를 이용해 채팅 내역 싹 가져오기
    completions = ChatbotCompletionSerializer(many=True, read_only=True)

    class Meta:
        model = ChatbotSessions
        fields = ["id", "title", "question", "using_model", "created_at", "completions"]


class ChatbotCompletionRequestSerializer(serializers.Serializer[dict[str, str]]):
    """유저가 AI에게 보내는 채팅 메시지를 검증"""

    message = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="AI에게 보낼 질문 메시지",
    )
