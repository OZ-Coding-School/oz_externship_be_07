from typing import Any

from rest_framework import serializers

from apps.subject.choices import StudentEnrollmentRequestsStatus
from apps.users.models.models import User


class EnrollmentUserSerializer(serializers.Serializer[User]):
    # 수강생 등록 요청한 유저 데이터
    class Meta:
        model = User
        fields = ["id", "email", "name", "birthday", "gender"]



class EnrollmentCohortSerializer(serializers.Serializer[Any]):
    # 수강생 등록 요청한 기수 데이터
    id = serializers.IntegerField()
    number = serializers.CharField()



class EnrollmentCourseSerializer(serializers.Serializer[Any]):
    # 수강생 등록 요청한 강의 데이터
    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()



class AdminUserEnrollmentSerializer(serializers.ModelSerializer[StudentEnrollmentRequestsStatus]):
    # 어드민 수강생 등록 요청 확인 데이터
    user = EnrollmentUserSerializer(read_only=True)
    cohort = EnrollmentCohortSerializer()
    course = EnrollmentCourseSerializer()
    status = StudentEnrollmentRequestsStatus(StudentEnrollmentRequestsStatus)

    class Meta:
        model = StudentEnrollmentRequestsStatus
        fields = ["id", "user", "cohort", "course", "status", "created_at"]

