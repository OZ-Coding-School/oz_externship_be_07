from django.db import models

from apps.core.models import TimeStampModel
from apps.users.models import User


class OperationManager(TimeStampModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "operation_managers"
