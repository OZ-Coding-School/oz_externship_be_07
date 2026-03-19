from typing import Any

from django.db import transaction
from django.db.models import Avg, QuerySet
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.course_models import Course


class CohortService:
    @staticmethod
    @transaction.atomic
    def create_cohort(*, validated_data: dict[str, Any]) -> Cohort:
        cohort = Cohort.objects.create(
            course=validated_data["course"],
            number=validated_data["number"],
            max_student=validated_data["max_student"],
            start_date=validated_data["start_date"],
            end_date=validated_data["end_date"],
            status=validated_data.get("status", "PREPARING"),
        )
        return cohort

    @staticmethod
    def get_cohorts_by_course_id(*, course_id: int) -> QuerySet[Cohort]:
        return Cohort.objects.filter(course_id=course_id).order_by("number")

    @staticmethod
    @transaction.atomic
    def update_cohort(*, cohort_id: int, validated_data: dict[str, Any]) -> Cohort:
        cohort = get_object_or_404(Cohort, pk=cohort_id)

        for field, value in validated_data.items():
            setattr(cohort, field, value)

        cohort.save()
        return cohort

    @staticmethod
    def get_cohort_students(*, cohort_id: int) -> QuerySet[CohortStudent]:
        cohort = get_object_or_404(Cohort, pk=cohort_id)

        return CohortStudent.objects.filter(cohort=cohort).select_related("user").order_by("id")

    @staticmethod
    def get_cohort_avg_scores(*, course_id: int) -> list[dict[str, Any]]:
        get_object_or_404(Course, pk=course_id)

        cohorts = (
            Cohort.objects.filter(course_id=course_id)
            .annotate(avg_score=Coalesce(Avg("examdeployment__examsubmission__score"), 0.0))
            .order_by("number")
        )

        return [
            {
                "name": f"{cohort.number}기",
                "score": int(cohort.avg_score or 0),
            }
            for cohort in cohorts
        ]
