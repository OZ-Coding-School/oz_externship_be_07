from rest_framework import serializers

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
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = Withdrawal
        fields = [
            "id",
            "nickname",
            "role",
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
