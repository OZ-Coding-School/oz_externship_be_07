from typing import Any, Dict, Optional

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.subject.models import Cohort, Course
from apps.users.models import User
from apps.users.services.admin_user_search_services import get_user_course_data


# Course
class CourseSimpleSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag"]


# Cohort
class CohortSimpleSerializer(serializers.ModelSerializer[Cohort]):
    class Meta:
        model = Cohort
        fields = ["id", "number"]


# in_progress_course 필드에 사용할 시리얼라이저
class InProgressCourseSerializer(serializers.Serializer[str | dict[str, Cohort | Course]]):
    cohort = CohortSimpleSerializer()
    course = CourseSimpleSerializer()


class StudentManagerSerializer(serializers.ModelSerializer[User]):
    # 이제 이 필드는 단순 문자열이 아니라 위에서 만든 객체 모양을 따릅니다.
    in_progress_course = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
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

    @extend_schema_field(InProgressCourseSerializer)
    def get_in_progress_course(self, obj: User) -> Optional[Dict[str, Any]]:
        data = get_user_course_data(obj)

        if not data:
            return None

        return InProgressCourseSerializer(data).data
