from apps.subject.models import CohortStudent
from apps.users.models.models import User
from typing import Any


def get_user_course_data(user: User) -> dict[str, Any] | None:
    cohort_student = CohortStudent.objects.filter(user=user).select_related("cohort__course").last()

    if not cohort_student:
        return None

    return {"cohort": cohort_student.cohort, "course": cohort_student.cohort.course}
