from typing import Any, Dict

from rest_framework import serializers


class AdminEnrollmentAcceptSerializer(serializers.Serializer[Dict[str, Any]]):
    enrollments = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )
