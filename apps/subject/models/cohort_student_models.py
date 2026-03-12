from django.db import models

from apps.core.models import TimeStampModel
from apps.subject.models.cohort_models import Cohort
from apps.users.models.models import User


class CohortStudent(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)

    class Meta:
        db_table = "cohort_students"
