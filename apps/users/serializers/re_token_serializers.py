from typing import Any

from rest_framework import serializers


class ReTokenSerializer(serializers.Serializer[Any]):
    refresh_token = serializers.CharField(required=True)
