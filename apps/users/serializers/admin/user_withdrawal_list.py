from rest_framework import serializers

from apps.users.models.models import User, Withdrawal


class AdminUserWithdrawalUserSerializer(serializers.ModelSerializer[Withdrawal]):
    class Meta:
        model = User
        fields = ["id", "name", "nickname", "role", "email"]


class AdminUserWithdrawalListSerializer(serializers.ModelSerializer[Withdrawal]):
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)

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
