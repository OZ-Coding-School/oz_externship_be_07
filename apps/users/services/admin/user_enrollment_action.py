from django.db import transaction
from django.utils import timezone

from apps.subject.models.cohort_student_models import CohortStudent
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.choices import EnrollmentStatus


def accept_enrollment_requests(enrollment_ids: list[int]) -> int:
    with transaction.atomic():
        requests = list(
            EnrollmentRequest.objects.filter(id__in=enrollment_ids, status=EnrollmentStatus.PENDING).select_related(
                "cohort", "user"
            )
        )

        if not requests:
            return 0

        now = timezone.now()
        cohort_students_to_create = []

        for req in requests:
            req.status = EnrollmentStatus.ACCEPTED
            req.accepted_at = now

            cohort_students_to_create.append(CohortStudent(cohort=req.cohort, user=req.user))

        EnrollmentRequest.objects.bulk_update(requests, ["status", "accepted_at"])

        CohortStudent.objects.bulk_create(cohort_students_to_create, ignore_conflicts=True)

    return len(requests)


def reject_enrollment_requests(enrollment_ids: list[int]) -> int:
    """
    대기 중인 수강 신청 건들을 반려합니다.
    """
    updated_count = EnrollmentRequest.objects.filter(id__in=enrollment_ids, status=EnrollmentStatus.PENDING).update(
        status=EnrollmentStatus.REJECTED
    )

    return updated_count
