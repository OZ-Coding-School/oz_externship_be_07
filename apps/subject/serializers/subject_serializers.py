from typing import Any

from rest_framework import serializers

from apps.exams.models.exam_submission_models import ExamSubmission
from apps.subject.models.subject_models import Subject


class SubjectCreateRequestSerializer(serializers.Serializer[Any]):
    course_id = serializers.IntegerField()
    title = serializers.CharField(max_length=30)
    number_of_days = serializers.IntegerField(min_value=1)
    number_of_hours = serializers.IntegerField(min_value=1)
    thumbnail_img_url = serializers.CharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
    )


class SubjectCreateResponseSerializer(serializers.ModelSerializer[Subject]):
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = (
            "id",
            "course_id",
            "title",
            "number_of_days",
            "number_of_hours",
            "thumbnail_img_url",
            "status",
        )

    def get_status(self, obj: Subject) -> str:
        return str(obj.status).lower()


class SubjectListItemSerializer(serializers.ModelSerializer[Subject]):
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = (
            "id",
            "course_id",
            "title",
            "status",
            "thumbnail_img_url",
        )

    def get_status(self, obj: Subject) -> str:
        return str(obj.status).lower()


class SubjectUpdateRequestSerializer(serializers.Serializer[Any]):
    title = serializers.CharField(max_length=30, required=False)
    number_of_days = serializers.IntegerField(min_value=1, required=False)
    number_of_hours = serializers.IntegerField(min_value=1, required=False)
    thumbnail_img_url = serializers.CharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    status = serializers.BooleanField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs:
            raise serializers.ValidationError("수정할 데이터가 없습니다.")
        return attrs


class SubjectDetailResponseSerializer(serializers.ModelSerializer[Subject]):
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = (
            "id",
            "course_id",
            "title",
            "number_of_days",
            "number_of_hours",
            "thumbnail_img_url",
            "status",
        )

    def get_status(self, obj: Subject) -> str:
        return str(obj.status).lower()


class SubjectScatterPointSerializer(serializers.ModelSerializer[ExamSubmission]):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ExamSubmission
        fields = [
            "duration",
            "score",
        ]

    def get_duration(self, obj: ExamSubmission) -> float:
        duration = obj.created_at - obj.started_at
        hours = duration.total_seconds() / 3600
        return round(hours, 1)
