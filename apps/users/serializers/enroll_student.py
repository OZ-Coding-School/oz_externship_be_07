from rest_framework import serializers

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.cohort_student_models import CohortStudent


class EnrollStudentSerializer(serializers.Serializer):
    cohort_id = serializers.IntegerField(
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다.", "invalid": "올바른 숫자를 입력해주세요."},
    )

    def validate_cohort_id(self, value: int) -> int:
        """기수가 실제로 존재하는지 확인"""
        if not Cohort.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 기수 ID입니다.")
        return value

    def save(self, **kwargs: any) -> CohortStudent:
        """수강생 등록 로직 실행"""
        user = kwargs.get("user")
        cohort_id = self.validated_data["cohort_id"]

        # get_or_create로 중복 신청 방지
        enrollment, created = CohortStudent.objects.get_or_create(user=user, cohort_id=cohort_id)
        return enrollment
