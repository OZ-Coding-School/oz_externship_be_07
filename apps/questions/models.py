from django.conf import settings  # 1팀의 User 모델 참조용
from django.db import models

from apps.core.models import TimeStampModel


class QuestionCategories(TimeStampModel):

    name = models.CharField(max_length=15)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    class Meta:
        db_table = "question_categories"
        verbose_name = "질문 카테고리"


class Questions(TimeStampModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(QuestionCategories, on_delete=models.PROTECT)
    title = models.CharField(max_length=50)
    content = models.TextField()
    view_count = models.IntegerField(default=0)

    class Meta:
        db_table = "questions"
        verbose_name = "질문"


class QuestionAiAnswers(TimeStampModel):
    questions = models.OneToOneField(Questions, on_delete=models.CASCADE, related_name="ai_answers")
    output = models.TextField()
    using_model = models.CharField(max_length=50)

    class Meta:
        db_table = "question_ai_answers"
        verbose_name = "자동 질문 답변"


class QuestionImages(TimeStampModel):
    questions = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="images")
    img_url = models.CharField(max_length=255)

    class Meta:
        db_table = "question_images"
        verbose_name = "질문 이미지"


class Answers(TimeStampModel):
    questions = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    is_adopted = models.BooleanField(default=False)

    class Meta:
        db_table = "answers"
        verbose_name = "답변"


class AnswerComments(TimeStampModel):
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()

    class Meta:
        db_table = "answer_comments"
        verbose_name = "답변 내용"


class AnswerImages(TimeStampModel):
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE, related_name="images")
    img_url = models.CharField(max_length=255)

    class Meta:
        db_table = "answer_images"
        verbose_name = "답변 이미지"
