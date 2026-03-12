from django.db import models

from apps.core.models import TimeStampModel
from apps.subject.models.choices import CohortStatus, StudentEnrollmentRequestsStatus
from apps.users.models.models import User


class EnrollmentRequest(TimeStampModel):
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default=StudentEnrollmentRequestsStatus.PENDING, choices=StudentEnrollmentRequestsStatus)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "enrollment_requests"
