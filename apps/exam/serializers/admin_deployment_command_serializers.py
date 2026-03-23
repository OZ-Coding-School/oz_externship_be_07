from typing import Any

from rest_framework import serializers

from apps.exam.models.exam_deployment_models import ExamDeployment


class ExamDeploymentCreateSerializer(serializers.ModelSerializer[ExamDeployment]):
    exam_id = serializers.IntegerField(write_only=True, min_value=1)
    cohort_id = serializers.IntegerField(write_only=True, min_value=1)
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

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        open_at = data.get("open_at")
        close_at = data.get("close_at")

        if open_at and close_at and open_at >= close_at:
            raise serializers.ValidationError("종료 일시는 시작 일시 이후여야 합니다.")

        return data


class ExamDeploymentCreateResponseSerializer(serializers.Serializer[dict[str, Any]]):
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

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        open_at = data.get("open_at", getattr(self.instance, "open_at", None))
        close_at = data.get("close_at", getattr(self.instance, "close_at", None))

        if open_at and close_at and open_at >= close_at:
            raise serializers.ValidationError("종료 일시는 시작 일시 이후여야 합니다.")

        return data


class ExamDeploymentUpdateResponseSerializer(serializers.Serializer[dict[str, Any]]):
    deployment_id = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.CharField()
    close_at = serializers.CharField()
    updated_at = serializers.CharField()


class ExamDeploymentStatusUpdateSerializer(serializers.Serializer[dict[str, Any]]):
    status = serializers.CharField()

    def validate_status(self, value: str) -> str:
        normalized = value.lower()
        allowed = {"activated", "deactivated"}

        if normalized not in allowed:
            raise serializers.ValidationError("유효하지 않은 상태 값입니다.")

        return normalized


class ExamDeploymentStatusUpdateResponseSerializer(serializers.Serializer[dict[str, Any]]):
    deployment_id = serializers.IntegerField()
    status = serializers.CharField()


class ExamDeploymentDeleteResponseSerializer(serializers.Serializer[dict[str, Any]]):
    deployment_id = serializers.IntegerField()
