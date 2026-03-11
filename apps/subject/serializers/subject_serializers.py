from rest_framework import serializers

from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.subject_models import Subject


class SubjectCreateRequestSerializer(serializers.Serializer):
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


class SubjectCreateResponseSerializer(serializers.ModelSerializer):
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


class SubjectListItemSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        model = Subject
        fields = (
            "id",
            "course_id",
            "title",
            "status",
            "thumbnail_img_url",
        )


class SubjectUpdateRequestSerializer(serializers.Serializer):
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

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("수정할 데이터가 없습니다.")
        return attrs


class SubjectDetailResponseSerializer(serializers.ModelSerializer):
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


class SubjectScatterPointSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    class Meta:
        model = ExamSubmission
        fields = [
            "time",
            "score",
        ]

    def get_time(self, obj):
        if obj.created_at and obj.started_at:
            duration = obj.created_at - obj.started_at
            hours = duration.total_seconds() / 3600
            return round(hours, 1)
        return 0.0


class ErrorResponseSerializer(serializers.Serializer):
    error_detail = serializers.CharField()
