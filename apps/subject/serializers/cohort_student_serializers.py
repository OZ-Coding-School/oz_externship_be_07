from typing import Any

from rest_framework import serializers


class StudentSubjectScoreItemSerializer(serializers.Serializer[Any]):
    subject = serializers.CharField()
    score = serializers.IntegerField()
