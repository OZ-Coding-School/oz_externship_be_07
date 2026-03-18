from typing import Any

from rest_framework import serializers

from apps.users.choices import UserRole


class AdminUserRoleUpdateSerializer(serializers.Serializer[dict[str, Any]]):
    role = serializers.ChoiceField(choices=UserRole.choices, required=True)
    cohort_id = serializers.IntegerField(required=False)
    assigned_courses = serializers.ListField(child=serializers.IntegerField(), required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        role = attrs.get("role")
        cohort_id = attrs.get("cohort_id")
        assigned_courses = attrs.get("assigned_courses")

        if role in [UserRole.TA, UserRole.STUDENT]:
            if not cohort_id:
                raise serializers.ValidationError({"cohort_id": ["조교 또는 수강생 권한으로 변경 시 필수 필드입니다."]})

        elif role in [UserRole.LC, UserRole.OM]:
            if not assigned_courses:
                raise serializers.ValidationError(
                    {"assigned_courses": ["러닝코치 또는 운영매니저 권한으로 변경 시 필수 필드입니다."]}
                )

        return attrs
