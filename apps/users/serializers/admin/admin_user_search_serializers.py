from typing import Any

from rest_framework import serializers

from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.models.models import User


class AdminUserCourseSerializer(serializers.ModelSerializer[EnrollmentRequest]):
    course = serializers.SerializerMethodField()
    cohort = serializers.SerializerMethodField()

    class Meta:
        model = EnrollmentRequest
        fields = ["course", "cohort"]

    def get_course(self, obj: EnrollmentRequest) -> dict[str, Any]:
        return {"id": obj.cohort.course.id, "name": obj.cohort.course.name, "tag": obj.cohort.course.tag}

    def get_cohort(self, obj: EnrollmentRequest) -> dict[str, Any]:
        return {
            "id": obj.cohort.id,
            "number": obj.cohort.number,
            "status": obj.cohort.status,
            "start_date": obj.cohort.start_date,
            "end_date": obj.cohort.end_date,
        }


class AdminUserSearchListSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "email", "nickname", "name", "birthday", "status", "role", "created_at"]


class AdminUserSearchDetailSerializer(serializers.ModelSerializer[User]):
    assigned_courses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "gender",
            "status",
            "role",
            "profile_img_url",
            "assigned_courses",
            "created_at",
        ]

    def get_assigned_courses(self, obj: User) -> Any:
        enrollments = EnrollmentRequest.objects.filter(user=obj).select_related("cohort__course")
        return AdminUserCourseSerializer(enrollments, many=True).data
