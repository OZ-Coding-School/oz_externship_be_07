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
    new_role = role_data["role"]
    TrainingAssistant.objects.filter(user=user).delete()
    OperationManager.objects.filter(user=user).delete()
    LearningCoach.objects.filter(user=user).delete()
    CohortStudent.objects.filter(user=user).delete()  # type: ignore

    user.role = new_role
    user.save()

    # [STUDENT] 수강생
    if new_role == UserRole.STUDENT:
        CohortStudent.objects.create(user=user, cohort_id=role_data["cohort_id"])  # type: ignore

    # [TA] 조교
    elif new_role == UserRole.TA:
        cohort_id = role_data.get("cohort_id")

        if cohort_id is not None:
            TrainingAssistant.objects.create(user=user, cohort_id=int(cohort_id))

    # [LC] 러닝코치
    elif new_role == UserRole.LC:
        for course_id in role_data.get("assigned_courses", []):
            LearningCoach.objects.create(user=user, course_id=course_id)

    # [OM] 운영매니저
    elif new_role == UserRole.OM:
        OperationManager.objects.bulk_create(
            [OperationManager(user=user, course_id=cid) for cid in role_data.get("assigned_courses", [])]
        )
