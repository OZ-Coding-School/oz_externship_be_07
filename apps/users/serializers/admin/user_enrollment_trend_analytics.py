from typing import Any

from rest_framework import serializers


class StudentEnrollmentTrendItemSerializer(serializers.Serializer[dict[str, Any]]):
    period = serializers.CharField()
    count = serializers.IntegerField()


class StudentEnrollmentTrendResponseSerializer(serializers.Serializer[dict[str, Any]]):
    interval = serializers.ChoiceField(choices=["monthly", "yearly"])
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    total = serializers.IntegerField()
    items = StudentEnrollmentTrendItemSerializer(many=True)


class StudentEnrollmentTrendRequestSerializer(serializers.Serializer[dict[str, Any]]):
    interval = serializers.ChoiceField(choices=["monthly", "yearly"])
