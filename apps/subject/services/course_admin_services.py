from typing import Any

from rest_framework.exceptions import NotFound, ValidationError

from apps.subject.models.course_models import Course


class CourseAdminService:

    @staticmethod
    def create_course(data: dict[str, Any]) -> Course:
        return Course.objects.create(**data)

    @staticmethod
    def update_course(course_id: int, data: dict[str, Any]) -> Course:
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise NotFound("과정을 찾을 수 없습니다.")

        for attr, value in data.items():
            setattr(course, attr, value)

        course.save()
        return course

    @staticmethod
    def delete_course(course_id: int) -> dict[str, str]:
        course = Course.objects.filter(id=course_id).first()

        if not course:
            raise NotFound("과정을 찾을 수 없습니다.")

        course.delete()
        return {"detail": "과정이 삭제되었습니다."}
