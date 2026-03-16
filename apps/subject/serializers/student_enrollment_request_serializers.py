from rest_framework import serializers
from typing import Any

class StudentEnrollmentAcceptRequestSerializer(serializers.Serializer[Any]):
    enrollments = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=True,
        allow_empty=False,
    )


class StudentEnrollmentAcceptResponseSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()


class StudentEnrollmentAcceptErrorResponseSerializer(serializers.Serializer[Any]):
    error_detail = serializers.DictField(required=False)