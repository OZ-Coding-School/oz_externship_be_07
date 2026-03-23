from typing import Any

from rest_framework import serializers

from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.choices import EnrollmentStatus


class EnrollStudentSerializer(serializers.Serializer[Any]):
    cohort_id = serializers.IntegerField(required=True)

    def validate_cohort_id(self, value: int) -> int:
        """필드 단위 검증: 기수 존재 여부 확인"""
        from apps.subject.models.cohort_models import Cohort

        if not Cohort.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 기수 ID입니다.")
        return value

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        request = self.context.get("request")
        if not request:
            return data

        user = request.user
        cohort_id: int | None = data.get("cohort_id")

        if cohort_id is None:
            return data

        enrollment = EnrollmentRequest.objects.filter(user=user, cohort_id=cohort_id).first()

        if enrollment:
            if enrollment.status == EnrollmentStatus.PENDING:
                raise serializers.ValidationError({"detail": "현재 신청 내역이 존재합니다."})

            elif enrollment.status == EnrollmentStatus.ACCEPTED:
                raise serializers.ValidationError({"detail": "이미 등록된 기수입니다."})

        return data

    def save(self, **kwargs: Any) -> EnrollmentRequest:
        user = kwargs.get("user")
        cohort_id = self.validated_data["cohort_id"]
        request_obj, _ = EnrollmentRequest.objects.update_or_create(
            user=user, cohort_id=cohort_id, defaults={"status": EnrollmentStatus.PENDING}
        )
        return request_obj
