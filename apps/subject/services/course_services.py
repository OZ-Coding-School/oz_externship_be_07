from apps.subject.models.course_models import Course


class CourseService:
    @staticmethod
    def get_course_list() -> list[Course]:
        return list(Course.objects.all().order_by("id"))