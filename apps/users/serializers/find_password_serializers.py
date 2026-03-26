from typing import Any, Dict

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class PasswordFindSerializer(serializers.Serializer[Dict[str, Any]]):
    email_token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value: str) -> str:
        validate_password(value)
        return value
