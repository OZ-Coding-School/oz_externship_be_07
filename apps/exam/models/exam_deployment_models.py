from django.db import models

from apps.core.models import TimeStampModel
from apps.exam.models.choices import DeploymentStatus
from apps.subject.models.cohort_models import Cohort
from apps.exam.models.exam_models import Exam
from apps.subject.models.cohort_models import Cohort


class ExamDeployment(TimeStampModel):
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    duration_time = models.SmallIntegerField(default=60)
    access_code = models.CharField(max_length=64)
    open_at = models.DateTimeField()
    close_at = models.DateTimeField()
    questions_snapshot_json = models.JSONField()
    status = models.CharField(max_length=20, default="PENDING", choices=DeploymentStatus)

    class Meta:
        db_table = "exam_deployments"
