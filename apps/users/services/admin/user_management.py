from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.subject.models.leaning_coach_models import LearningCoach
from apps.subject.models.operation_manager_models import OperationManager
from apps.subject.models.traning_assistant_models import TrainingAssistant
from apps.users.choices import EnrollmentStatus, UserRole
from apps.users.models.models import User


def delete_user_by_admin(account_id: int) -> int:
    """
    어드민 권한으로 유저를 삭제하고 삭제된 PK를 반환합니다.
    """
    user = get_object_or_404(User, id=account_id)
    user_pk = user.pk
    user.delete()
    return user_pk


@transaction.atomic
def update_user_role(user_id: int, role_data: dict[str, Any]) -> None:
    user = get_object_or_404(User, id=user_id)
    new_role = role_data["role"]
    TrainingAssistant.objects.filter(user=user).delete()
    OperationManager.objects.filter(user=user).delete()
    LearningCoach.objects.filter(user=user).delete()
    CohortStudent.objects.filter(user=user).delete()

    user.role = new_role
    user.save()

    # [STUDENT] 수강생
    if new_role == UserRole.STUDENT:
        CohortStudent.objects.create(user=user, cohort_id=role_data["cohort_id"])

    # [TA] 조교
    elif new_role == UserRole.TA:
        cohort_id = role_data.get("cohort_id")

        if cohort_id is not None:
            TrainingAssistant.objects.create(user=user, cohort_id=int(cohort_id))

    # [LC] 러닝코치
    elif new_role == UserRole.LC:
        LearningCoach.objects.bulk_create(
            [LearningCoach(user=user, course_id=cid) for cid in role_data.get("assigned_courses", [])]
        )

    # [OM] 운영매니저
    elif new_role == UserRole.OM:
        OperationManager.objects.bulk_create(
            [OperationManager(user=user, course_id=cid) for cid in role_data.get("assigned_courses", [])]
        )


def accept_enrollment_requests(enrollment_ids: list[int]) -> int:
    with transaction.atomic():
        requests = list(
            EnrollmentRequest.objects.filter(id__in=enrollment_ids, status=EnrollmentStatus.PENDING).select_related(
                "cohort", "user"
            )
        )

        if not requests:
            return 0

        user_ids = [req.user_id for req in requests]
        cohort_ids = [req.cohort_id for req in requests]
        existing_enrollments = set(
            CohortStudent.objects.filter(user_id__in=user_ids, cohort_id__in=cohort_ids).values_list(
                "user_id", "cohort_id"
            )
        )

        now = timezone.now()
        cohort_students_to_create = []
        users_to_update = []

        for req in requests:
            req.status = EnrollmentStatus.ACCEPTED
            req.accepted_at = now

            if req.user.role != UserRole.STUDENT:
                req.user.role = UserRole.STUDENT
                if req.user not in users_to_update:
                    users_to_update.append(req.user)

            if (req.user_id, req.cohort_id) not in existing_enrollments:
                cohort_students_to_create.append(CohortStudent(cohort=req.cohort, user=req.user))

        EnrollmentRequest.objects.bulk_update(requests, ["status", "accepted_at"])

        if users_to_update:
            User.objects.bulk_update(users_to_update, ["role"])

        if cohort_students_to_create:
            CohortStudent.objects.bulk_create(cohort_students_to_create)

    return len(requests)


def reject_enrollment_requests(enrollment_ids: list[int]) -> int:
    """
    대기 중인 수강 신청 건들을 반려합니다.
    """
    updated_count = EnrollmentRequest.objects.filter(id__in=enrollment_ids, status=EnrollmentStatus.PENDING).update(
        status=EnrollmentStatus.REJECTED
    )

    return updated_count
