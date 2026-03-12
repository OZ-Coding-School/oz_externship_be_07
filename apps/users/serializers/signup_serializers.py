from typing import Any, Dict

from rest_framework import serializers

from apps.users.models.models import User


class SignUpSerializer(serializers.ModelSerializer["User"]):
    password = serializers.CharField(write_only=True)
    email_token = serializers.CharField(write_only=True)
    sms_token = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "gender",
            "email_token",
            "sms_token",
        ]
        extra_kwargs: Dict[str, Any] = {
            "password": {"write_only": True},
        }
