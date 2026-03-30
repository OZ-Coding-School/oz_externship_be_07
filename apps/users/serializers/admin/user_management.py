from typing import Any

from rest_framework import serializers

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.choices import EnrollmentStatus
from apps.users.models.models import User


class EnrollmentUserSerializer(serializers.ModelSerializer[User]):
    """수강생 등록 요청한 유저 데이터"""

    class Meta:
        model = User
        fields = ["id", "email", "name", "birthday", "gender"]


class EnrollmentCohortSerializer(serializers.ModelSerializer[Cohort]):
    """수강생 등록 요청한 기수 데이터"""

    class Meta:
        model = Cohort
        fields = ["id", "number"]


class EnrollmentCourseSerializer(serializers.ModelSerializer[Course]):
    """수강생 등록 요청한 강의 데이터"""

    class Meta:
        model = Course
        fields = ["id", "name", "tag"]


class AdminUserEnrollmentSerializer(serializers.ModelSerializer[EnrollmentRequest]):
    """어드민 수강생 등록 요청 목록 조회 API용"""

    user = EnrollmentUserSerializer(read_only=True)
    cohort = EnrollmentCohortSerializer(read_only=True)
    course = EnrollmentCourseSerializer(source="cohort.course", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = EnrollmentRequest
        fields = ["id", "user", "cohort", "course", "status", "created_at"]

    def get_status(self, obj: EnrollmentRequest) -> str:
        accepted_states = ("APPROVED", EnrollmentStatus.ACCEPTED)
        if obj.status in accepted_states:
            return EnrollmentStatus.ACCEPTED

        return obj.status


class AdminEnrollmentAcceptSerializer(serializers.Serializer[dict[str, Any]]):
    enrollments = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )


class AdminEnrollmentRejectSerializer(serializers.Serializer[dict[str, Any]]):
    enrollments = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )


from typing import Any

from rest_framework import serializers

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.users.choices import UserRole


class AdminUserRoleUpdateSerializer(serializers.Serializer[Any]):
    role = serializers.ChoiceField(choices=UserRole.choices)
    cohort_id = serializers.IntegerField(required=False, allow_null=True)
    assigned_courses = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        role = attrs.get("role")
        cohort_id = attrs.get("cohort_id")
        assigned_courses = attrs.get("assigned_courses", [])

        # 1. [STUDENT, TA] 기수(Cohort) 존재 여부 검증
        if role in [UserRole.STUDENT, UserRole.TA]:
            if not cohort_id:
                raise serializers.ValidationError({"cohort_id": "기수 정보가 필요합니다."})
            if not Cohort.objects.filter(id=cohort_id).exists():
                raise serializers.ValidationError({"cohort_id": "존재하지 않는 기수 ID입니다."})

        # 2. [LC, OM] 코스(Course) 존재 여부 검증
        if role in [UserRole.LC, UserRole.OM]:
            if not assigned_courses:
                raise serializers.ValidationError({"assigned_courses": "코스 정보가 필요합니다."})

            # 보낸 코스 ID들이 존재하는지 확인
            existing_count = Course.objects.filter(id__in=assigned_courses).count()
            if existing_count != len(set(assigned_courses)):
                raise serializers.ValidationError({"assigned_courses": "존재하지 않는 코스 ID가 포함되어 있습니다."})

        return attrs


class StudentEnrollmentTrendItemSerializer(serializers.Serializer[dict[str, Any]]):
    period = serializers.CharField()
    count = serializers.IntegerField()


class StudentEnrollmentTrendResponseSerializer(serializers.Serializer[dict[str, Any]]):
    interval = serializers.ChoiceField(choices=["monthly", "yearly"])
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    total = serializers.IntegerField()
    items = StudentEnrollmentTrendItemSerializer(many=True)


class StudentEnrollmentTrendRequestSerializer(serializers.Serializer[dict[str, Any]]):
    interval = serializers.ChoiceField(choices=["monthly", "yearly"])
