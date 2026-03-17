from typing import Any, Dict

from django.utils import timezone
from rest_framework import serializers

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.subject.models.cohort_models import Cohort


# =========================================================
# 쪽지시험 배포 생성 API
# POST /api/v1/admin/exams/deployments
# =========================================================
class ExamDeploymentCreateSerializer(serializers.ModelSerializer[ExamDeployment]):  # [수정] 이름 및 [ExamDeployment]
    exam = serializers.PrimaryKeyRelatedField(
        queryset=Exam.objects.all(),
        write_only=True,
    )
    cohort = serializers.PrimaryKeyRelatedField(
        queryset=Cohort.objects.all(),
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
            "exam",
            "cohort",
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


# =========================================================
# 쪽지시험 배포 목록 조회 API
# GET /api/v1/admin/exams/deployments
# =========================================================
class ExamDeploymentListQuerySerializer(serializers.Serializer[Dict[str, Any]]):
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    size = serializers.IntegerField(required=False, default=10, min_value=1)
    search_keyword = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.IntegerField(required=False, min_value=1)
    cohort = serializers.IntegerField(required=False, min_value=1)
    sort = serializers.CharField(required=False, allow_blank=True)
    order = serializers.ChoiceField(
        choices=["asc", "desc"],
        required=False,
    )


class ExamDeploymentListSerializer(serializers.Serializer[Dict[str, Any]]):  # [수정]
    id = serializers.IntegerField()
    submit_count = serializers.IntegerField()
    avg_score = serializers.FloatField()
    status = serializers.CharField()
    exam = serializers.DictField()
    subject = serializers.DictField()
    cohort = serializers.DictField()
    created_at = serializers.CharField()


class ExamDeploymentListResponseSerializer(serializers.Serializer[Dict[str, Any]]):  # [수정]
    count = serializers.IntegerField()
    previous = serializers.CharField(allow_null=True)
    next = serializers.CharField(allow_null=True)
    results = ExamDeploymentListSerializer(many=True)


# =========================================================
# 쪽지시험 배포 상세 조회 API
# GET /api/v1/admin/exams/deployments/{deployment}
# =========================================================
class ExamDeploymentDetailSerializer(serializers.Serializer[Dict[str, Any]]):  # [수정]
    id = serializers.IntegerField()
    exam_access_url = serializers.CharField()
    access_code = serializers.CharField()
    cohort = serializers.DictField()
    submit_count = serializers.IntegerField()
    not_submitted_count = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.CharField()
    close_at = serializers.CharField()
    created_at = serializers.CharField()
    exam = serializers.DictField()
    subject = serializers.DictField()


# =========================================================
# 쪽지시험 배포 정보 수정 API
# PATCH /api/v1/admin/exams/deployments/{deployment}
# =========================================================
class ExamDeploymentUpdateSerializer(serializers.ModelSerializer[ExamDeployment]):  # [수정] [ExamDeployment]
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


class ExamDeploymentUpdateResponseSerializer(serializers.Serializer[Dict[str, Any]]):  # [수정]
    deployment = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.CharField()
    close_at = serializers.CharField()
    updated_at = serializers.CharField()


# =========================================================
# 쪽지시험 배포 on/off API
# PATCH /api/v1/admin/exams/deployments/{deployment}/status
# =========================================================
class ExamDeploymentStatusUpdateSerializer(serializers.Serializer[Dict[str, Any]]):  # [수정]
    status = serializers.ChoiceField(choices=["Activated", "Deactivated"])


class ExamDeploymentStatusUpdateResponseSerializer(serializers.Serializer[Dict[str, Any]]):  # [수정]
    deployment = serializers.IntegerField()
    status = serializers.CharField()


# =========================================================
# 쪽지시험 배포 삭제 API
# DELETE /api/v1/admin/exams/deployments/{deployment}
# =========================================================
class ExamDeploymentDeleteResponseSerializer(serializers.Serializer[Dict[str, Any]]):  # [수정]
    detail = serializers.CharField()


# =========================================================
# 공통 에러 응답
# =========================================================
class ErrorDetailSerializer(serializers.Serializer[Dict[str, Any]]):  # [수정]
    error_detail = serializers.CharField()
