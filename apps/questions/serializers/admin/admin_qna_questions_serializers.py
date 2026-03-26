from typing import Any

from rest_framework import serializers

from apps.questions.models import Questions


# 어드민 질의응답 목록 조회
class AdminQuestionListSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    question_id = serializers.IntegerField(source="id")
    category_path = serializers.SerializerMethodField()
    nickname = serializers.CharField(source="author.nickname", read_only=True)
    content_preview = serializers.SerializerMethodField()
    has_answer = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Questions
        fields = [
            "question_id",
            "title",
            "category_path",
            "content_preview",
            "nickname",
            "view_count",
            "has_answer",
            "created_at",
            "updated_at",
        ]

    def get_category_path(self, obj: Questions) -> str:
        path = []
        current: Any = obj.category
        while current:
            path.append(current.name)
            current = current.parent
        return " > ".join(reversed(path))

    def get_content_preview(self, obj: Questions) -> str:
        if obj.content and len(obj.content) > 50:
            return obj.content[:50] + "..."
        return obj.content

    def get_has_answer(self, obj: Questions) -> bool:
        return obj.answers.exists()


class AdminQuestionListResponseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    total_count = serializers.IntegerField()
    questions = AdminQuestionListSerializer(many=True)
