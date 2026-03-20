import json
from typing import Any, Dict

from rest_framework import serializers

from apps.exam.models.choices import QuestionType
from apps.exam.models.exam_question_models import ExamQuestion


class ExamQuestionCreateSerializer(serializers.Serializer[Dict[str, Any]]):
    type = serializers.ChoiceField(choices=QuestionType.choices)
    question = serializers.CharField(max_length=255)
    prompt = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    options = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
    )
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    correct_answer = serializers.JSONField()
    point = serializers.IntegerField(min_value=0, max_value=100)
    explanation = serializers.CharField()


class ExamQuestionUpdateSerializer(ExamQuestionCreateSerializer):
    pass


class ExamQuestionResponseSerializer(serializers.ModelSerializer[ExamQuestion]):
    question_id = serializers.IntegerField(source="id")
    exam_id = serializers.IntegerField(source="exam_id")
    correct_answer = serializers.JSONField(source="answer")
    options = serializers.SerializerMethodField()

    class Meta:
        model = ExamQuestion
        fields = [
            "question_id",
            "exam_id",
            "type",
            "question",
            "prompt",
            "options",
            "blank_count",
            "correct_answer",
            "point",
            "explanation",
        ]

    def get_options(self, obj: ExamQuestion) -> Any:
        if not obj.options_json:
            return None
        try:
            return json.loads(obj.options_json)
        except ValueError:
            return None


class ExamQuestionDeleteResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    exam_id = serializers.IntegerField()
    question_id = serializers.IntegerField()


class ErrorDetailSerializer(serializers.Serializer[Dict[str, str]]):
    error_detail = serializers.CharField()
