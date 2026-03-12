import json

from rest_framework import serializers

from apps.exam.models.choices import QuestionType
from apps.exam.models.exam_question_models import ExamQuestion


class ExamQuestionCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=QuestionType)
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

    def validate(self, data):
        return data

    def validate_type(self, value):
        return value.upper()


class ExamQuestionUpdateSerializer(ExamQuestionCreateSerializer):
    pass


class ExamQuestionResponseSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    type = serializers.CharField()
    question = serializers.CharField()
    prompt = serializers.CharField(allow_null=True, allow_blank=True)
    options = serializers.ListField(child=serializers.CharField(), allow_null=True)
    blank_count = serializers.IntegerField(allow_null=True)
    correct_answer = serializers.JSONField()
    point = serializers.IntegerField()
    explanation = serializers.CharField()


def serialize_question_response(question: ExamQuestion) -> dict:
    options = None
    if question.options_json:
        try:
            options = json.loads(question.options_json)
        except (ValueError, TypeError, json.JSONDecodeError):
            options = None

    return {
        "question_id": question.id,
        "type": question.type.lower(),
        "question": question.question,
        "options": options,
        "prompt": question.prompt,
        "blank_count": question.blank_count,
        "correct_answer": question.answer,
        "point": question.point,
        "explanation": question.explanation,
    }


class ExamQuestionDeleteResponseSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
