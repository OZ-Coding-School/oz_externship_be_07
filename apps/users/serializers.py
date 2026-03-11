from rest_framework import serializers

from .models import User


class SignUpSerializer(serializers.ModelSerializer["User"]):
    password = serializers.CharField(write_only=True, source="hashed_password")
    email_token = serializers.CharField(write_only=True)
    sms_token = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "password",
            "nickname",
            "name",
            "birthday",
            "gender",
            "email",
            "email_token",
            "phone_number",
            "sms_token",
        ]
