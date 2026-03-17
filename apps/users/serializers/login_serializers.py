from typing import Any

from rest_framework import serializers


class LoginSerializer(serializers.Serializer[dict[str, Any]]):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
