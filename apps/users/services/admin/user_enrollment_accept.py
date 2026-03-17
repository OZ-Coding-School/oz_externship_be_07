from apps.subject.models.enrollment_request_models import EnrollmentRequest


def accept_enrollment_requests(enrollment_ids: list[int]) -> int:
    """
    대기 중인 수강 신청 건들을 승인 상태로 변경하고 변경된 건수를 반환합니다.
    """
    updated_count = EnrollmentRequest.objects.filter(id__in=enrollment_ids, status="PENDING").update(status="ACCEPTED")

    return updated_count
