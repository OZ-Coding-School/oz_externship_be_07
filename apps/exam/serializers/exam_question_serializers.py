import json
from typing import Any

from rest_framework import serializers

from apps.exam.models.choices import QuestionType
from apps.exam.models.exam_question_models import ExamQuestion


class ExamQuestionSerializer(serializers.Serializer[dict[str, Any]]):
    type = serializers.ChoiceField(choices=QuestionType.choices)
    question = serializers.CharField(max_length=255)
    prompt = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    options = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
    )
    blank_count = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    correct_answer = serializers.JSONField()
    point = serializers.IntegerField(min_value=0, max_value=10)
    explanation = serializers.CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        question_type = attrs["type"]
        correct_answer = attrs["correct_answer"]
        options = attrs.get("options")
        blank_count = attrs.get("blank_count")

        if (
            question_type
            in [
                QuestionType.SINGLE_CHOICE,
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.OX,
                QuestionType.ORDERING,
            ]
            and not options
        ):
            raise serializers.ValidationError({"options": "이 문제 유형에는 선택지가 필요합니다."})

        if (
            question_type
            in [
                QuestionType.SHORT_ANSWER,
                QuestionType.FILL_BLANK,
            ]
            and options is not None
        ):
            raise serializers.ValidationError({"options": "이 문제 유형에는 선택지를 받을 수 없습니다."})

        if question_type in [
            QuestionType.SINGLE_CHOICE,
            QuestionType.OX,
            QuestionType.SHORT_ANSWER,
        ] and not isinstance(correct_answer, str):
            raise serializers.ValidationError({"correct_answer": "이 문제 유형의 정답은 문자열이어야 합니다."})

        if question_type in [
            QuestionType.MULTIPLE_CHOICE,
            QuestionType.ORDERING,
        ] and not isinstance(correct_answer, list):
            raise serializers.ValidationError({"correct_answer": "이 문제 유형의 정답은 리스트여야 합니다."})

        if question_type == QuestionType.FILL_BLANK:
            if blank_count is None or blank_count < 1:
                raise serializers.ValidationError({"blank_count": "빈칸형 문제는 1개 이상의 빈칸 수가 필요합니다."})

        if question_type in [QuestionType.SINGLE_CHOICE, QuestionType.OX]:
            if options is None:
                raise serializers.ValidationError({"options": "이 문제 유형에는 선택지가 필요합니다."})

            if correct_answer not in options:
                raise serializers.ValidationError({"correct_answer": "정답이 선택지에 없습니다."})

        if question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.ORDERING]:
            if not correct_answer:
                raise serializers.ValidationError({"correct_answer": "정답 리스트가 비어 있습니다."})

            if options is None:
                raise serializers.ValidationError({"options": "이 문제 유형에는 선택지가 필요합니다."})

            for answer in correct_answer:
                if answer not in options:
                    raise serializers.ValidationError({"correct_answer": "선택지에 없는 값이 포함되어 있습니다."})

        return attrs


class ExamQuestionCreateResponseSerializer(serializers.ModelSerializer[ExamQuestion]):
    correct_answer = serializers.JSONField(source="answer")
    options = serializers.SerializerMethodField()

    class Meta:
        model = ExamQuestion
        fields = [
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


class ExamQuestionUpdateResponseSerializer(serializers.ModelSerializer[ExamQuestion]):
    question_id = serializers.IntegerField(source="id")
    correct_answer = serializers.JSONField(source="answer")
    options = serializers.SerializerMethodField()

    class Meta:
        model = ExamQuestion
        fields = [
            "question_id",
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


class ExamQuestionDeleteResponseSerializer(serializers.Serializer[dict[str, Any]]):
    exam_id = serializers.IntegerField()
    question_id = serializers.IntegerField()


class ErrorDetailSerializer(serializers.Serializer[dict[str, str]]):
    error_detail = serializers.CharField()
