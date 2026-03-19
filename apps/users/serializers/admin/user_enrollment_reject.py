from typing import Any

from rest_framework import serializers


class AdminEnrollmentRejectSerializer(serializers.Serializer[dict[str, Any]]):
    enrollments = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )
