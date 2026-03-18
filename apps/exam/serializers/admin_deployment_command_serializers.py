from typing import Any, Dict

from django.utils import timezone
from rest_framework import serializers

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.subject.models.cohort_models import Cohort


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
            raise serializers.ValidationError("종료 일시는 시작 일시 이후여야 합니다.")

        if open_at and open_at < now:
            raise serializers.ValidationError("시작 시간은 현재 시간보다 이전일 수 없습니다.")

        return data


class ExamDeploymentCreateResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    pk = serializers.IntegerField()


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
        now = timezone.now()

        if open_at and close_at and open_at >= close_at:
            raise serializers.ValidationError("종료 일시는 시작 일시 이후여야 합니다.")

        if open_at and open_at < now:
            raise serializers.ValidationError("시작 시간은 현재 시간보다 이전일 수 없습니다.")

        return data


class ExamDeploymentUpdateResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    deployment_id = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class ExamDeploymentStatusUpdateSerializer(serializers.Serializer[Dict[str, Any]]):
    status = serializers.ChoiceField(choices=["activated", "deactivated"])


class ExamDeploymentStatusUpdateResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    deployment_id = serializers.IntegerField()
    status = serializers.CharField()


class ExamDeploymentDeleteResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    detail = serializers.CharField()
