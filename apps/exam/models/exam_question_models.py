from django.db import models

from apps.core.models import TimeStampModel
from apps.exam.models.choices import QuestionType
from apps.exam.models.exam_models import Exam


class ExamQuestion(TimeStampModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    prompt = models.TextField(null=True, blank=True)
    blank_count = models.SmallIntegerField(null=True, blank=True)
    options_json = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=20, default=QuestionType.SINGLE_CHOICE , choices=QuestionType)
    answer = models.JSONField()
    point = models.SmallIntegerField()
    explanation = models.TextField()

    class Meta:
        db_table = "exam_questions"
