from django.test import TestCase

from apps.subject.models.course_models import Course
from apps.subject.services.course_services import CourseService


class CourseServiceTests(TestCase):
    def test_get_course_list_returns_all_courses_ordered_by_id(self) -> None:
        course1 = Course.objects.create(name="A", tag="1")
        course2 = Course.objects.create(name="B", tag="2")

        result = CourseService.get_course_list()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, course1.id)
        self.assertEqual(result[1].id, course2.id)
