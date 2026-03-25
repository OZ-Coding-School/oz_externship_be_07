from typing import Any

from rest_framework import serializers

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course


class CourseSimpleSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag", "thumbnail_img_url"]


class CohortSimpleSerializer(serializers.ModelSerializer[Cohort]):
    class Meta:
        model = Cohort
        fields = ["id", "number", "start_date", "end_date", "status"]


class MyEnrolledCourseSerializer(serializers.Serializer[Any]):
    cohort = CohortSimpleSerializer()
    course = CourseSimpleSerializer()
