from rest_framework import serializers

class StudentEnrollmentAcceptRequestSerializer(serializers.Serializer):
    enrollments = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=True,
        allow_empty=False,
    )


class StudentEnrollmentAcceptResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class StudentEnrollmentAcceptErrorResponseSerializer(serializers.Serializer):
    error_detail = serializers.DictField(required=False)