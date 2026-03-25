from rest_framework import serializers

from apps.users.models.models import User, Withdrawal


class AdminUserSimpleSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "name", "nickname", "role", "email"]


class AdminUserWithdrawalListSerializer(serializers.ModelSerializer[Withdrawal]):
    user = AdminUserSimpleSerializer(read_only=True)

    class Meta:
        model = Withdrawal
        fields = [
            "id",
            "user",
            "reason",
            "created_at",
        ]


class AdminUserWithdrawalDetailSerializer(AdminUserWithdrawalListSerializer):
    assigned_courses = serializers.ReadOnlyField()

    class Meta(AdminUserWithdrawalListSerializer.Meta):
        fields = AdminUserWithdrawalListSerializer.Meta.fields + [
            "reason_detail",
            "due_date",
            "assigned_courses",
        ]
