from rest_framework import serializers

from apps.subject.models import Cohort, Course, EnrollmentRequest
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
        if obj.status == "APPROVED":
            return "ACCEPTED"
        return obj.status
