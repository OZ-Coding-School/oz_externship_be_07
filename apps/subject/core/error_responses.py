from typing import Any

from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer[Any]):
    error_detail = serializers.CharField()
