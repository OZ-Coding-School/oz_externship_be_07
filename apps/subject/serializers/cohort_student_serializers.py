from typing import Any

from rest_framework import serializers


# 어드민 페이지 수강생 목록 조회 API
class StudentListQuerySerializer(serializers.Serializer[Any]):
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, default=10)
    search = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=[
            "activated",
            "deactivated",
            "withdrew",
        ],
        required=False,
    )


class StudentInProgressCohortSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    number = serializers.IntegerField()


class StudentInProgressCourseSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()


class StudentInProgressCourseWrapperSerializer(serializers.Serializer[Any]):
    cohort = StudentInProgressCohortSerializer()
    course = StudentInProgressCourseSerializer()


class StudentListItemSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    nickname = serializers.CharField()
    name = serializers.CharField()
    phone_number = serializers.CharField()
    birthday = serializers.DateField()
    status = serializers.ChoiceField(
        choices=["ACTIVATED", "DEACTIVATED", "WITHDREW"],
    )
    role = serializers.ChoiceField(
        choices=["U", "TA", "OM", "ADMIN", "ST"],
    )
    in_progress_course = StudentInProgressCourseWrapperSerializer(allow_null=True)
    created_at = serializers.DateTimeField()


class StudentListResponseSerializer(serializers.Serializer[Any]):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = StudentListItemSerializer(many=True)


# 학생별 과목 점수 조회 API
class StudentSubjectScoreItemSerializer(serializers.Serializer[Any]):
    subject = serializers.CharField()
    score = serializers.IntegerField()


# 어드민 기수별 수강생 목록 조회 API
class CohortStudentItemSerializer(serializers.Serializer[Any]):
    value = serializers.CharField()
    label = serializers.CharField()  # type: ignore[assignment]

