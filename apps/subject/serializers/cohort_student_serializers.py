from typing import Any

from rest_framework import serializers


# 학생별 과목 점수 조회 API
class StudentSubjectScoreItemSerializer(serializers.Serializer[Any]):
    subject = serializers.CharField()
    score = serializers.IntegerField()
