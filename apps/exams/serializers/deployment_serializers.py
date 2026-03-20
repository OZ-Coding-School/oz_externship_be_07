from typing import Any

from rest_framework import serializers


class StringOrStringListField(serializers.Field[Any, Any, Any, Any]):
    def to_representation(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return value
        raise serializers.ValidationError("문자열, 문자열 리스트, null만 허용됩니다.")


class DeploymentListQuerySerializer(serializers.Serializer[dict[str, Any]]):
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    status = serializers.ChoiceField(
        choices=["all", "done", "pending"],
        required=False,
        default="all",
    )


class DeploymentSubjectSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    thumbnail_img_url = serializers.CharField(allow_null=True)


class DeploymentExamSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    thumbnail_img_url = serializers.CharField()
    subject = DeploymentSubjectSerializer()


class DeploymentExamInfoSerializer(serializers.Serializer[dict[str, Any]]):
    status = serializers.ChoiceField(choices=["done", "pending"])
    score = serializers.IntegerField(allow_null=True)
    correct_answer_count = serializers.IntegerField(allow_null=True)


class DeploymentListItemSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    submission_id = serializers.IntegerField(allow_null=True)
    exam = DeploymentExamSerializer()
    question_count = serializers.IntegerField()
    total_score = serializers.IntegerField()
    exam_info = DeploymentExamInfoSerializer()
    is_done = serializers.BooleanField()
    duration_time = serializers.IntegerField()


class DeploymentListResponseSerializer(serializers.Serializer[dict[str, Any]]):
    page = serializers.IntegerField()
    has_next = serializers.BooleanField()
    results = DeploymentListItemSerializer(many=True)


class DeploymentQuestionItemSerializer(serializers.Serializer[dict[str, Any]]):
    question_id = serializers.IntegerField()
    number = serializers.IntegerField()
    type = serializers.ChoiceField(
        choices=[
            "single_choice",
            "multiple_choice",
            "ox",
            "short_answer",
            "ordering",
            "fill_blank",
        ]
    )
    question = serializers.CharField()
    point = serializers.IntegerField()
    prompt = serializers.CharField(allow_null=True)
    blank_count = serializers.IntegerField(allow_null=True)
    options = serializers.ListField(
        child=serializers.CharField(),
        allow_null=True,
    )
    answer_input = StringOrStringListField()


class DeploymentDetailResponseSerializer(serializers.Serializer[dict[str, Any]]):
    exam_id = serializers.IntegerField()
    exam_name = serializers.CharField()
    duration_time = serializers.IntegerField()
    elapsed_time = serializers.IntegerField()
    cheating_count = serializers.IntegerField()
    questions = DeploymentQuestionItemSerializer(many=True)


class DeploymentCheckCodeRequestSerializer(serializers.Serializer[dict[str, Any]]):
    code = serializers.CharField()


class DeploymentStatusResponseSerializer(serializers.Serializer[dict[str, Any]]):
    exam_status = serializers.CharField()
    force_submit = serializers.BooleanField()
