from typing import Any

# from apps.users.models.models import User
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.questions.models import Questions

from .models import ChatbotCompletions, ChatbotSessions

User = get_user_model()


class ChatbotSessionCreateSerializer(serializers.ModelSerializer[ChatbotSessions]):
    """
    AI 챗봇 세션 생성 <POST>
    /api/v1/chatbot/sessions

    """

    user: serializers.PrimaryKeyRelatedField[Any] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    question: serializers.PrimaryKeyRelatedField[Any] = serializers.PrimaryKeyRelatedField(
        queryset=Questions.objects.all(),
    )

    class Meta:
        model = ChatbotSessions
        fields = ["user", "question", "title", "using_model"]


class SupportSessionCreateSerializer(serializers.ModelSerializer[ChatbotSessions]):
    """
    AI 시스템 챗봇 세션 생성 <POST>
    /api/v1/chatbot/support
    """

    class Meta:
        model = ChatbotSessions
        fields = ["title", "using_model"]


class ChatbotSessionReadSerializer(serializers.ModelSerializer[ChatbotSessions]):
    """
    <GET> //api/v1/chatbot/sessions (목록 조회)
    <POST> 세션 성공 성공 시 응답
    """

    question_id: serializers.IntegerField = serializers.IntegerField(
        source="question.id", read_only=True, allow_null=True
    )

    class Meta:
        model = ChatbotSessions
        fields = ["id", "user_id", "question_id", "title", "using_model", "created_at", "updated_at"]
        read_only_fields = fields


class ChatbotCompletionRequestSerializer(serializers.Serializer[Any]):
    """
    <POST> /api/v1/chatbot/sessions/{session_id}/completions
    사용자 메시지 입력 검증용
    """

    message: serializers.CharField = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={"required": "이 필드는 필수 항목입니다.", "blank": "이 필드는 blank 일 수 없습니다."},
    )


class ChatbotCompletionReadSerializer(serializers.ModelSerializer[ChatbotCompletions]):
    """
    <GET> /api/v1/chatbot/sessions/{session_id}/completions
    챗봇 대화 내역 조회 응답용
    """

    class Meta:
        model = ChatbotCompletions
        fields = ["id", "message", "role", "created_at"]
        read_only_fields = fields
