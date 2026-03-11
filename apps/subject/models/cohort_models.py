from django.db import models

from apps.core.models import TimeStampModel
from apps.subject.models.choices import CohortStatus, StudentEnrollmentRequestsStatus
from apps.subject.models.choices import CohortStatus
from apps.subject.models.course_models import Course


class Cohort(TimeStampModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    number = models.SmallIntegerField()
    max_student = models.SmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, default="PENDING", choices=CohortStatus)

    class Meta:
        db_table = "cohorts"
        unique_together = (("course", "number"),)
        indexes = [
            models.Index(fields=["course", "number"]),
        ]
