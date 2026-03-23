from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.users.models.models import User


class CourseSimpleSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag"]


class CohortSimpleSerializer(serializers.ModelSerializer[Cohort]):
    class Meta:
        model = Cohort
        fields = ["id", "number"]


class InProgressCourseSerializer(serializers.Serializer[dict[str, Any]]):
    cohort = CohortSimpleSerializer()
    course = CourseSimpleSerializer()


class StudentManagerSerializer(serializers.ModelSerializer[User]):
    in_progress_course = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields: list[str] = [
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "status",
            "role",
            "in_progress_course",
            "created_at",
        ]

    @extend_schema_field(InProgressCourseSerializer(allow_null=True))
    def get_in_progress_course(self, obj: User) -> dict[str, Any] | None:
        last_enrollment = obj.cohort_students.order_by("-id").first()  # type: ignore

        if not last_enrollment:
            return None

        return InProgressCourseSerializer(
            {"cohort": last_enrollment.cohort, "course": last_enrollment.cohort.course}
        ).data
