from typing import Any

from rest_framework import serializers

from apps.chatbot.models import ChatbotCompletions, ChatbotSessions


class ChatbotSessionSerializer(serializers.ModelSerializer[ChatbotSessions]):
    """세션 생성/목록 조회 응답용 — 명세서 필드: id, user, question_id, title, using_model, created_at, updated_at"""

    question_id = serializers.IntegerField(source="question.id", read_only=True, allow_null=True)

    class Meta:
        model = ChatbotSessions
        fields = ["id", "user", "question_id", "title", "using_model", "created_at", "updated_at"]
        read_only_fields = fields


class ChatbotCompletionSerializer(serializers.ModelSerializer[ChatbotCompletions]):
    """대화내역 조회 응답용 — 명세서 필드: id, message, role, created_at"""

    class Meta:
        model = ChatbotCompletions
        fields = ["id", "message", "role", "created_at"]
        read_only_fields = fields


class ChatbotCompletionRequestSerializer(serializers.Serializer[dict[str, str]]):
    """유저가 AI에게 보내는 채팅 메시지 검증"""

    message = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "이 필드는 blank일 수 없습니다.",
        },
    )
