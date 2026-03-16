from typing import Any

from rest_framework import serializers

from apps.subject.models.enrollment_request_models import EnrollmentRequest


class StudentEnrollmentAcceptRequestSerializer(serializers.Serializer[EnrollmentRequest]):
    enrollments = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=True,
        allow_empty=False,
    )


class StudentEnrollmentAcceptResponseSerializer(serializers.Serializer[EnrollmentRequest]):
    detail = serializers.CharField()


class StudentEnrollmentAcceptErrorResponseSerializer(serializers.Serializer[EnrollmentRequest]):
    error_detail = serializers.DictField(required=False)
