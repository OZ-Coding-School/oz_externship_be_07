from typing import Any, Dict

from rest_framework import serializers

from apps.exam.models.choices import QuestionType


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

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data

    def validate_type(self, value: str) -> str:
        return value.upper()


class ExamQuestionUpdateSerializer(ExamQuestionCreateSerializer):
    pass


class ExamQuestionResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    question_id = serializers.IntegerField()
    type = serializers.CharField()
    question = serializers.CharField()
    prompt = serializers.CharField(allow_null=True, allow_blank=True)
    options = serializers.ListField(child=serializers.CharField(), allow_null=True)
    blank_count = serializers.IntegerField(allow_null=True)
    correct_answer = serializers.JSONField()
    point = serializers.IntegerField()
    explanation = serializers.CharField()


class ExamQuestionDeleteResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    exam_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
