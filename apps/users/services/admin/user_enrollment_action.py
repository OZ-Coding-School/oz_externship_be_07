from django.db import transaction
from django.utils import timezone

from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.choices import EnrollmentStatus, UserRole  # ✅ UserRole 추가
from apps.users.models.models import User  # ✅ User 모델 임포트


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
