from django.db import models

from apps.core.models import TimeStampModel
from apps.users.models.models import User


class TrainingAssistant(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)

    class Meta:
        db_table = "training_assistants"
