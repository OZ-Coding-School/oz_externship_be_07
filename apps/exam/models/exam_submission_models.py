from django.db import models

from apps.core.models import TimeStampModel
from apps.users.models import User
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.users.models import User


class ExamSubmission(TimeStampModel):
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    deployment = models.ForeignKey(ExamDeployment, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    cheating_count = models.SmallIntegerField()
    answers_json = models.JSONField()
    score = models.SmallIntegerField()
    correct_answer_count = models.SmallIntegerField()

    class Meta:
        db_table = "exam_submissions"
