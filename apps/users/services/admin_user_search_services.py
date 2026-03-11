from apps.subject.models import Cohort, CohortStudent, Course
from apps.users.models import User


def get_user_course_data(user: User) -> str | dict[str, Cohort | Course]:
    cohort_student = CohortStudent.objects.filter(user=user).select_related("cohort__course").last()

    if not cohort_student:
        return "정보 없음"

    return {"cohort": cohort_student.cohort, "course": cohort_student.cohort.course}
