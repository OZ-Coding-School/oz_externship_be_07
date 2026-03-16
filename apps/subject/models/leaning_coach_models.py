from django.db import models

from apps.core.models import TimeStampModel
from apps.users.models.models import User
from apps.subject.models.course_models import Course


class LearningCoach(TimeStampModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects: models.Manager["LearningCoach"] = models.Manager()

    class Meta:
        db_table = "learning_coachs"
