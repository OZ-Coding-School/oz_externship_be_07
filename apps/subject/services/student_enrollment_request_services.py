from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.subject.models.choices import StudentEnrollmentRequestsStatus
from apps.subject.models.enrollment_request_models import EnrollmentRequest


class StudentEnrollmentRequestService:
    @staticmethod
    @transaction.atomic
    def accept_enrollments(*, enrollment_ids: list[int]) -> None:
        enrollments = EnrollmentRequest.objects.select_for_update().filter(
            id__in=enrollment_ids
        )

        found_ids = set(enrollments.values_list("id", flat=True))
        requested_ids = set(enrollment_ids)

        not_found_ids = sorted(requested_ids - found_ids)
        if not_found_ids:
            raise ValidationError(
                detail={
                    "enrollments": [
                        f"존재하지 않는 수강생 등록 요청 ID가 포함되어 있습니다: {not_found_ids}"
                    ]
                }
            )

        not_pending_ids = sorted(
            enrollments.exclude(
                status=StudentEnrollmentRequestsStatus.PENDING
            ).values_list("id", flat=True)
        )
        if not_pending_ids:
            raise ValidationError(
                detail={
                    "enrollments": [
                        f"승인 가능한 상태(PENDING)가 아닌 요청이 포함되어 있습니다: {not_pending_ids}"
                    ]
                }
            )

        enrollments.update(
            status=StudentEnrollmentRequestsStatus.ACCEPTED,
            accepted_at=timezone.now(),
        )