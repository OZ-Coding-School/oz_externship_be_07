from typing import Any, Dict

from django.utils import timezone
from rest_framework import serializers

from apps.exam.models.choices import DeploymentStatus
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.subject.models.cohort_models import Cohort


class ExamSimpleSerializer(serializers.Serializer[Dict[str, Any]]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    thumbnail_img_url = serializers.CharField(required=False, allow_null=True)


class SubjectSimpleSerializer(serializers.Serializer[Dict[str, Any]]):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CohortSimpleSerializer(serializers.Serializer[Dict[str, Any]]):
    id = serializers.IntegerField()
    number = serializers.IntegerField()
    display = serializers.CharField(required=False)
    name = serializers.CharField()


class ExamDeploymentCreateSerializer(serializers.ModelSerializer[ExamDeployment]):
    exam_id = serializers.PrimaryKeyRelatedField(
        queryset=Exam.objects.all(),
        source="exam",
        write_only=True,
    )
    cohort_id = serializers.PrimaryKeyRelatedField(
        queryset=Cohort.objects.all(),
        source="cohort",
        write_only=True,
    )
    duration_time = serializers.IntegerField(
        default=60,
        required=False,
        min_value=1,
        max_value=32767,
    )

    class Meta:
        model = ExamDeployment
        fields = [
            "exam_id",
            "cohort_id",
            "duration_time",
            "open_at",
            "close_at",
        ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        open_at = data.get("open_at")
        close_at = data.get("close_at")
        now = timezone.now()

        if open_at and close_at and open_at >= close_at:
            raise serializers.ValidationError({"error_detail": "종료 일시는 시작 일시 이후여야 합니다."})

        if open_at and open_at < now:
            raise serializers.ValidationError({"error_detail": "시작 시간은 현재 시간보다 이전일 수 없습니다."})

        exam = data.get("exam")
        cohort = data.get("cohort")

        if exam and cohort:
            if ExamDeployment.objects.filter(exam=exam, cohort=cohort).exists():
                raise serializers.ValidationError({"error_detail": "동일한 조건의 배포가 이미 존재합니다."})

        return data


class ExamDeploymentCreateResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    pk = serializers.IntegerField()


class ExamDeploymentListQuerySerializer(serializers.Serializer[Dict[str, Any]]):
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    size = serializers.IntegerField(required=False, default=10, min_value=1)
    search_keyword = serializers.CharField(required=False, allow_blank=True)
    subject_id = serializers.IntegerField(required=False, min_value=1)
    cohort_id = serializers.IntegerField(required=False, min_value=1)
    sort = serializers.CharField(required=False, allow_blank=True)
    order = serializers.ChoiceField(
        choices=["asc", "desc"],
        required=False,
    )


class ExamDeploymentListSerializer(serializers.Serializer[Dict[str, Any]]):
    id = serializers.IntegerField()
    submit_count = serializers.IntegerField()
    avg_score = serializers.FloatField()
    status = serializers.CharField()
    exam = ExamSimpleSerializer()
    subject = SubjectSimpleSerializer()
    cohort = CohortSimpleSerializer()
    created_at = serializers.DateTimeField()


class ExamDeploymentListResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    count = serializers.IntegerField()
    previous = serializers.CharField(allow_null=True, required=False)
    next = serializers.CharField(allow_null=True, required=False)
    results = ExamDeploymentListSerializer(many=True)


class ExamDeploymentDetailSerializer(serializers.Serializer[Dict[str, Any]]):
    id = serializers.IntegerField()
    exam_access_url = serializers.CharField()
    access_code = serializers.CharField()
    submit_count = serializers.IntegerField()
    not_submitted_count = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    exam = ExamSimpleSerializer()
    subject = SubjectSimpleSerializer()
    cohort = CohortSimpleSerializer()


class ExamDeploymentUpdateSerializer(serializers.ModelSerializer[ExamDeployment]):
    duration_time = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=32767,
    )

    class Meta:
        model = ExamDeployment
        fields = [
            "duration_time",
            "open_at",
            "close_at",
        ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        open_at = data.get("open_at", getattr(self.instance, "open_at", None))
        close_at = data.get("close_at", getattr(self.instance, "close_at", None))

        if open_at and close_at and open_at >= close_at:
            raise serializers.ValidationError({"error_detail": "종료 일시는 시작 일시 이후여야 합니다."})

        return data


class ExamDeploymentUpdateResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    id = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class ExamDeploymentStatusUpdateSerializer(serializers.Serializer[Dict[str, Any]]):
    status = serializers.ChoiceField(choices=DeploymentStatus.choices)


class ExamDeploymentStatusUpdateResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    id = serializers.IntegerField()
    status = serializers.CharField()


class ExamDeploymentDeleteResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    detail = serializers.CharField()


class ErrorDetailSerializer(serializers.Serializer[Dict[str, Any]]):
    error_detail = serializers.CharField()
