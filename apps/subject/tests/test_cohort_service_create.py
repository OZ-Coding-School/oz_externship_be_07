from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.services.cohort_services import CohortService


class CohortServiceCreateTests(TestCase):
    course: Course

    @classmethod
    def setUpTestData(cls) -> None:
        cls.course = Course.objects.create(
            name="백엔드",
            tag="BE1",
            description="백엔드 과정",
        )

    def test_creates_cohort_successfully(self) -> None:
        cohort = CohortService.create_cohort(
            validated_data={
                "course": self.course,
                "number": 15,
                "max_student": 30,
                "start_date": date(2025, 11, 1),
                "end_date": date(2026, 4, 30),
                "status": "PREPARING",
            }
        )

        self.assertIsInstance(cohort, Cohort)
        self.assertEqual(cohort.course_id, self.course.id)
        self.assertEqual(cohort.number, 15)
        self.assertEqual(cohort.max_student, 30)
        self.assertEqual(cohort.status, "PREPARING")

    def test_creates_cohort_with_default_status_when_status_is_missing(self) -> None:
        cohort = CohortService.create_cohort(
            validated_data={
                "course": self.course,
                "number": 16,
                "max_student": 25,
                "start_date": date(2025, 11, 1),
                "end_date": date(2026, 4, 30),
            }
        )

        self.assertEqual(cohort.status, "PREPARING")