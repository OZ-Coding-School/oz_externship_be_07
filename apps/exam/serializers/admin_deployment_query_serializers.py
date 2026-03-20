from typing import Any

from rest_framework import serializers


class ExamSimpleSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    thumbnail_img_url = serializers.CharField()


class SubjectSimpleSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CourseSimpleSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()


class CohortSimpleSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    number = serializers.IntegerField()
    display = serializers.CharField()
    course = CourseSimpleSerializer()


class ExamDeploymentListQuerySerializer(serializers.Serializer[dict[str, Any]]):
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    size = serializers.IntegerField(required=False, default=10, min_value=1)
    search_keyword = serializers.CharField(required=False, allow_blank=True)
    subject_id = serializers.IntegerField(required=False, min_value=1)
    cohort_id = serializers.IntegerField(required=False, min_value=1)
    sort = serializers.CharField(required=False, allow_blank=True)
    order = serializers.ChoiceField(
        choices=["asc", "desc"],
        required=False,
        default="desc",
    )


class ExamDeploymentListItemSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    submit_count = serializers.IntegerField()
    avg_score = serializers.FloatField()
    status = serializers.CharField()
    exam = ExamSimpleSerializer()
    subject = SubjectSimpleSerializer()
    cohort = CohortSimpleSerializer()
    created_at = serializers.CharField()


class ExamDeploymentListResponseSerializer(serializers.Serializer[dict[str, Any]]):
    count = serializers.IntegerField()
    previous = serializers.CharField(allow_null=True, required=False)
    next = serializers.CharField(allow_null=True, required=False)
    results = ExamDeploymentListItemSerializer(many=True)


class ExamDeploymentDetailSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    exam_access_url = serializers.CharField()
    access_code = serializers.CharField()
    cohort = CohortSimpleSerializer()
    submit_count = serializers.IntegerField()
    not_submitted_count = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.CharField()
    close_at = serializers.CharField()
    created_at = serializers.CharField()
    exam = ExamSimpleSerializer()
    subject = SubjectSimpleSerializer()
