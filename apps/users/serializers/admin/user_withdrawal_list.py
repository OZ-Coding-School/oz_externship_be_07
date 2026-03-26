from typing import Any

from rest_framework import serializers

from apps.users.models.models import User, Withdrawal


class AdminUserSimpleSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "email", "name", "role", "birthday"]


class AdminUserDetailSimpleSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "email", "nickname", "name", "gender", "role", "status", "profile_img_url", "created_at"]


class AdminUserWithdrawalListSerializer(serializers.ModelSerializer[Withdrawal]):
    user = AdminUserSimpleSerializer(read_only=True)
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    withdrawn_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Withdrawal
        fields = ["id", "user", "reason", "reason_display", "withdrawn_at"]


class AdminUserWithdrawalDetailSerializer(AdminUserWithdrawalListSerializer):
    user: Any = AdminUserSimpleSerializer(read_only=True)
    assigned_courses = serializers.ReadOnlyField()

    class Meta(AdminUserWithdrawalListSerializer.Meta):
        fields = AdminUserWithdrawalListSerializer.Meta.fields + [
            "reason_detail",
            "due_date",
            "assigned_courses",
        ]
