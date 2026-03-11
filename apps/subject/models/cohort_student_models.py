from django.db import models

from apps.core.models import TimeStampModel
from apps.users.models import User


class CohortStudent(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)

    class Meta:
        db_table = "cohort_students"
