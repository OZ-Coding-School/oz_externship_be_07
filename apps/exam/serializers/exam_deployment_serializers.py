from typing import Any, Dict, Optional

from django.utils import timezone
from rest_framework import serializers

from apps.exam.models.exam_models import Exam


# 1. 생성용 (POST)
class ExamCreateSerializer(serializers.ModelSerializer[Exam]):
    thumbnail_img = serializers.ImageField(write_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "thumbnail_img", "thumbnail_img_url"]
        read_only_fields = ["id", "thumbnail_img_url"]

    def create(self, validated_data: Dict[str, Any]) -> Exam:
        thumbnail_img = validated_data.pop("thumbnail_img")
        # S3 업로드 경로 예시 (요구사항 반영)
        validated_data["thumbnail_img_url"] = (
            f"https://oz-externship.s3.ap-northeast-2.amazonaws.com/exams/{thumbnail_img.name}"
        )
        return super().create(validated_data)


# 2. 목록 조회용 (GET List)
class ExamListSerializer(serializers.ModelSerializer[Exam]):
    subject_name = serializers.CharField(source="subject.title", read_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject_name", "created_at", "updated_at"]


# 3. 상세 조회용 (GET Detail)
class ExamDetailSerializer(serializers.ModelSerializer[Exam]):
    subject = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "thumbnail_img_url", "created_at", "updated_at"]

    def get_subject(self, obj: Exam) -> Dict[str, Any]:
        return {"id": obj.subject.id, "title": obj.subject.title}


# 4. 수정용 (PUT)
class ExamUpdateSerializer(serializers.ModelSerializer[Exam]):
    thumbnail_img = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "thumbnail_img", "thumbnail_img_url"]
        read_only_fields = ["id", "thumbnail_img_url"]

    def update(self, instance: Exam, validated_data: Dict[str, Any]) -> Exam:
        thumbnail_img = validated_data.pop("thumbnail_img", None)
        if thumbnail_img:
            instance.thumbnail_img_url = (
                f"https://oz-externship.s3.ap-northeast-2.amazonaws.com/exams/{thumbnail_img.name}"
            )
        return super().update(instance, validated_data)


class ExamDeleteRequestSerializer(serializers.ModelSerializer[Exam]):
    class Meta:
        model = Exam
        fields = ["id"]


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
