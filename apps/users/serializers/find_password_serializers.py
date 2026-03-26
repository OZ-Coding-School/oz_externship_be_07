from typing import Any, Dict

from rest_framework import serializers


class PasswordFindSerializer(serializers.Serializer[Dict[str, Any]]):
    email_token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
