from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.course_models import Course
from apps.subject.serializers.cohort_serializers import (
    CohortCreateRequestSerializer,
    CohortUpdateRequestSerializer,
)


class CohortCreateRequestSerializerTests(TestCase):
    course: Course

    @classmethod
    def setUpTestData(cls) -> None:
        cls.course = Course.objects.create(
            name="백엔드",
            tag="BE1",
            description="백엔드 과정",
        )

    def test_validates_successfully_with_valid_data(self) -> None:
        serializer = CohortCreateRequestSerializer(
            data={
                "course_id": self.course.id,
                "number": 15,
                "max_student": 30,
                "start_date": "2025-11-01",
                "end_date": "2026-04-30",
                "status": "PREPARING",
            }
        )

        is_valid = serializer.is_valid()

        self.assertTrue(is_valid, serializer.errors)

    def test_fails_when_end_date_is_not_after_start_date(self) -> None:
        serializer = CohortCreateRequestSerializer(
            data={
                "course_id": self.course.id,
                "number": 15,
                "max_student": 30,
                "start_date": "2025-11-01",
                "end_date": "2025-11-01",
                "status": "PREPARING",
            }
        )

        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("end_date", serializer.errors)

    def test_fails_when_status_is_invalid(self) -> None:
        serializer = CohortCreateRequestSerializer(
            data={
                "course_id": self.course.id,
                "number": 15,
                "max_student": 30,
                "start_date": "2025-11-01",
                "end_date": "2026-04-30",
                "status": "INVALID",
            }
        )

        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("status", serializer.errors)


class CohortUpdateRequestSerializerTests(TestCase):
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

    def test_validates_partial_update_when_dates_are_valid(self) -> None:
        serializer = CohortUpdateRequestSerializer(
            instance=self.cohort,
            data={"status": "IN_PROGRESS"},
            partial=True,
        )

        is_valid = serializer.is_valid()

        self.assertTrue(is_valid, serializer.errors)

    def test_fails_when_end_date_is_not_after_start_date(self) -> None:
        serializer = CohortUpdateRequestSerializer(
            instance=self.cohort,
            data={"end_date": "2025-10-01"},
            partial=True,
        )

        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("end_date", serializer.errors)