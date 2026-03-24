from typing import Any

from rest_framework import serializers

from apps.subject.models.cohort_student_models import CohortStudent
from apps.users.models.models import User, Withdrawal


class AdminUserWithdrawalUserSerializer(serializers.ModelSerializer[Withdrawal]):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "role",
            "birthday",
            "nickname",
            "gender",
            "status",
            "profile_img_url",
            "created_at",
        ]


class AdminUserWithdrawalListSerializer(serializers.ModelSerializer[Withdrawal]):
    user = AdminUserWithdrawalUserSerializer(read_only=True)
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    withdrawn_at = serializers.DateTimeField(source="created_at", read_only=True)
    assigned_courses = serializers.SerializerMethodField()

    class Meta:
        model = Withdrawal
        fields = [
            "id",
            "user",
            "assigned_courses",
            "reason",
            "reason_display",
            "reason_detail",
            "due_date",
            "withdrawn_at",
        ]

    def get_assigned_courses(self, obj: Withdrawal) -> list[dict[str, Any]]:
        if not obj.user:
            return []

        cohort_students = CohortStudent.objects.filter(user=obj.user).select_related("cohort", "cohort__course")
        return [
            {
                "course": {"id": cs.cohort.course.id, "name": cs.cohort.course.name, "tag": cs.cohort.course.tag},
                "cohort": {
                    "id": cs.cohort.id,
                    "number": cs.cohort.number,
                    "status": cs.cohort.status,
                    "start_date": cs.cohort.start_date,
                    "end_date": cs.cohort.end_date,
                },
            }
            for cs in cohort_students
        ]
