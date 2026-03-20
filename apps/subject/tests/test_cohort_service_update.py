from __future__ import annotations

from datetime import date

from django.http import Http404
from django.test import TestCase

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.services.cohort_services import CohortService


class CohortServiceUpdateTests(TestCase):
    course: Course
    cohort: Cohort

    @classmethod
    def setUpTestData(cls) -> None:
        cls.course = Course.objects.create(
            name="프론트엔드",
            tag="FE1",
            description="프론트엔드 과정",
        )
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=date(2025, 11, 1),
            end_date=date(2026, 4, 30),
            status="PREPARING",
        )

    def test_updates_cohort_successfully(self) -> None:
        updated = CohortService.update_cohort(
            cohort_id=self.cohort.id,
            validated_data={
                "max_student": 40,
                "status": "IN_PROGRESS",
            },
        )

        self.assertEqual(updated.id, self.cohort.id)
        self.assertEqual(updated.max_student, 40)
        self.assertEqual(updated.status, "IN_PROGRESS")

    def test_raises_404_when_cohort_does_not_exist(self) -> None:
        with self.assertRaises(Http404):
            CohortService.update_cohort(
                cohort_id=999999,
                validated_data={"status": "FINISHED"},
            )
