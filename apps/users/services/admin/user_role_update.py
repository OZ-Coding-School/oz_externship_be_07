from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.leaning_coach_models import LearningCoach
from apps.subject.models.operation_manager_models import OperationManager
from apps.subject.models.traning_assistant_models import TrainingAssistant
from apps.users.choices import UserRole
from apps.users.models.models import User


@transaction.atomic
def update_user_role(user_id: int, role_data: dict[str, Any]) -> None:
    user = get_object_or_404(User, id=user_id)
    new_role = str(role_data.get("role", ""))
    TrainingAssistant.objects.filter(user=user).delete()
    OperationManager.objects.filter(user=user).delete()
    LearningCoach.objects.filter(user=user).delete()
    CohortStudent.objects.filter(user=user).delete()  # type: ignore

    user = User.objects.get(id=user_id)
    user.role = new_role
    user.save()

    # [STUDENT] 수강생
    if new_role == UserRole.STUDENT:
        CohortStudent.objects.create(user=user, cohort_id=role_data["cohort_id"])  # type: ignore

    # [TA] 조교
    elif new_role == UserRole.TA:
        TrainingAssistant.objects.create(user=user, cohort_id=role_data["cohort_id"])

    # [LC] 러닝코치
    elif new_role == UserRole.LC:
        for course_id in role_data.get("assigned_courses", []):
            LearningCoach.objects.create(user=user, course_id=course_id)

    # [OM] 운영매니저
    elif new_role == UserRole.OM:
        for course_id in role_data.get("assigned_courses", []):
            OperationManager.objects.create(user=user, course_id=course_id)
