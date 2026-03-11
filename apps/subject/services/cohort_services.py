from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.course_models import Course


class CohortService:
    @staticmethod
    @transaction.atomic
    def create_cohort(*, validated_data: dict) -> Cohort:
        course = get_object_or_404(Course, pk=validated_data["course_id"])

        cohort = Cohort.objects.create(
            course=course,
            number=validated_data["number"],
            max_student=validated_data["max_student"],
            start_date=validated_data["start_date"],
            end_date=validated_data["end_date"],
            status=validated_data.get("status", "PREPARING"),
        )
        return cohort

    @staticmethod
    def get_cohorts_by_course_id(*, course_id: int):
        return Cohort.objects.filter(course_id=course_id).order_by("id")

    @staticmethod
    @transaction.atomic
    def update_cohort(*, cohort_id: int, validated_data: dict) -> Cohort:
        cohort = get_object_or_404(Cohort, pk=cohort_id)

        for field, value in validated_data.items():
            if field == "course_id":
                continue
            setattr(cohort, field, value)

        cohort.save()
        return cohort

    @staticmethod
    def get_cohort_students(*, cohort_id: int):
        cohort = get_object_or_404(Cohort, pk=cohort_id)

        return CohortStudent.objects.filter(cohort=cohort).select_related("user").order_by("id")
