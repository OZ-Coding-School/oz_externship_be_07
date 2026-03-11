from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import User


class SignUpSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        validated_data.pop("email_token")
        validated_data.pop("sms_token")

        password2 = validated_data.pop("hashed_password")
        validated_data["hashed_password"] = make_password(password2)

        return User.objects.create(**validated_data)
