from django.db import models

from apps.core.models import TimeStampModel
from apps.exam.models.choices import QuestionType
from apps.exam.models.exam_models import Exam


class ExamQuestion(TimeStampModel):
    # 실제 DB에는 생성되지 않지만, 분석 도구(mypy)에게 "이런 속성이 있다"고 알려주는 용도입니다.
    id: int
    exam_id: int
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    prompt = models.TextField(null=True, blank=True)
    blank_count = models.SmallIntegerField(null=True, blank=True)
    options_json = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=20, default=QuestionType.SINGLE_CHOICE, choices=QuestionType)
    answer = models.JSONField()
    point = models.SmallIntegerField()
    explanation = models.TextField()

    objects: models.Manager["ExamQuestion"] = models.Manager()

    class Meta:
        db_table = "exam_questions"
