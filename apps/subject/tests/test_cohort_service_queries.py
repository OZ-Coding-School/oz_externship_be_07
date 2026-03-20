from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.subject.models.cohort_models import Cohort
from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.course_models import Course
from apps.subject.services.cohort_services import CohortService
from apps.users.models.models import User


class CohortServiceQueryTests(TestCase):
    course: Course
    cohort1: Cohort
    cohort2: Cohort
    user1: User
    user2: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.course = Course.objects.create(
            name="데이터분석",
            tag="DA1",
            description="데이터 분석 과정",
        )
        cls.cohort1 = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=20,
            start_date=date(2025, 11, 1),
            end_date=date(2026, 4, 30),
            status="PREPARING",
        )
        cls.cohort2 = Cohort.objects.create(
            course=cls.course,
            number=2,
            max_student=25,
            start_date=date(2025, 12, 1),
            end_date=date(2026, 5, 30),
            status="IN_PROGRESS",
        )

        cls.user1 = User.objects.create_user(
            email="student1@example.com",
            password="1234",
            name="학생1",
            nickname="student01",
            phone_number="01011112222",
            gender="MALE",
            birthday=date(2000, 1, 1),
            role="USER",
        )
        cls.user2 = User.objects.create_user(
            email="student2@example.com",
            password="1234",
            name="학생2",
            nickname="student02",
            phone_number="01033334444",
            gender="FEMALE",
            birthday=date(2000, 1, 2),
            role="USER",
        )

        CohortStudent.objects.create(user=cls.user1, cohort=cls.cohort1)
        CohortStudent.objects.create(user=cls.user2, cohort=cls.cohort1)

    def test_returns_cohorts_ordered_by_number(self) -> None:
        cohorts = list(CohortService.get_cohorts_by_course_id(course_id=self.course.id))

        self.assertEqual(len(cohorts), 2)
        self.assertEqual(cohorts[0].number, 1)
        self.assertEqual(cohorts[1].number, 2)

    def test_returns_students_of_cohort(self) -> None:
        students = list(CohortService.get_cohort_students(cohort_id=self.cohort1.id))

        self.assertEqual(len(students), 2)
        self.assertEqual(students[0].user.nickname, "student01")
        self.assertEqual(students[1].user.nickname, "student02")

    def test_returns_avg_scores_as_zero_when_no_submission_exists(self) -> None:
        result = CohortService.get_cohort_avg_scores(course_id=self.course.id)

        self.assertEqual(
            result,
            [
                {"name": "1기", "score": 0},
                {"name": "2기", "score": 0},
            ],
        )