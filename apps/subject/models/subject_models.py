from django.db import models

from apps.core.models import TimeStampModel
from apps.subject.models.course_models import Course


class Subject(TimeStampModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    number_of_days = models.SmallIntegerField()
    number_of_hours = models.SmallIntegerField()
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "subjects"
        unique_together = (("course", "title"),)
        indexes = [
            models.Index(fields=["course", "title"]),
        ]
