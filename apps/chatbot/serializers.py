from typing import Any

from rest_framework import serializers


class ChatbotCompletionRequestSerializer(serializers.Serializer[Any]):
    """
    <POST> /api/v1/chatbot/sessions/{session_id}/completions
    사용자 메시지 입력 검증용
    """

    message: serializers.CharField = serializers.CharField(
        required=True,
        help_text="사용자 질문",
    )
    bot_type = serializers.CharField(
        required=False,
        default="qna",
        help_text="챗봇 타입 (qna 또는 support)",
    )
