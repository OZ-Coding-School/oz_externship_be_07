from django.utils import timezone

from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.choices import EnrollmentStatus


def accept_enrollment_requests(enrollment_ids: list[int]) -> int:
    """
    대기 중인 수강 신청 건들을 승인 상태로 변경하고 승인 시간을 기록합니다.
    """
    updated_count = EnrollmentRequest.objects.filter(id__in=enrollment_ids, status=EnrollmentStatus.PENDING).update(
        status=EnrollmentStatus.ACCEPTED, accepted_at=timezone.now()
    )

    return updated_count


def reject_enrollment_requests(enrollment_ids: list[int]) -> int:
    """
    대기 중인 수강 신청 건들을 반려합니다.
    """
    updated_count = EnrollmentRequest.objects.filter(id__in=enrollment_ids, status=EnrollmentStatus.PENDING).update(
        status=EnrollmentStatus.REJECTED
    )

    return updated_count
