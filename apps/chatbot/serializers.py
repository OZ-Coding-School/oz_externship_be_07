from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.questions.models import Questions

from .models import ChatbotSessions, ChatbotCompletions

User = get_user_model()


class ChatbotSessionSerializer(serializers.ModelSerializer):
    # """챗봇 세션 생성 및 조회용 시리얼라이저"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    question = serializers.PrimaryKeyRelatedField(
        queryset=Questions.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = ChatbotSessions
        fields = ["id", "user", "question", "title", "using_model", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    # def to_representation(self, instance):
    #     # """ API명세서 필드명  question, question_id """
    #     representation = super().to_representation(instance)
    #     representation["question_id"] = representation.pop("question")
    #     if instance.user:
    #         representation["user"] = instance.user.user.id
    #     return representation


class ChatbotMessageSerializer(serializers.ModelSerializer):
    # """챗봇 대화 내역 조회용 시리얼라이저 (GET) """
    role = serializers.CharField()

    class Meta:
        model = ChatbotCompletions
        fields = ["id", "message", "role", "created_at"]


class ChatbotCompletionRequestSerializer(serializers.Serializer):
    # """ 사용자 메시지 입력 검증용 시리얼라이저 (POST) """
    message = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={"required": "이 필드는 필수 항목입니다.", "blank": "이 필드는 blank 일 수 없습니다."}
    )
