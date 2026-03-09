from django.conf import settings  # 1팀의 User 모델 참조용
from django.db import models


class QuestionCategories(models.Model):
    CATEGORY_TYPES = (
        ("large", "대분류"),
        ("medium", "중분류"),
        ("small", "소분류"),
    )
    name = models.CharField(max_length=15)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question_categories"
        verbose_name = "질문 카테고리"


class Questions(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(QuestionCategories, on_delete=models.PROTECT)
    title = models.CharField(max_length=50)
    content = models.TextField()
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "questions"
        verbose_name = "질문"


class QuestionsAiAnswer(models.Model):
    questions = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="ai_answers")
    output = models.TextField()
    using_model = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "questions_ai_answers"
        verbose_name = "자동 질문 답변"


class QuestionsImages(models.Model):
    questions = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="images")
    img_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "questions_images"
        verbose_name = "질문 이미지"


class Answers(models.Model):
    questions = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    is_adopted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "answers"
        verbose_name = "답변"


class AnswerComments(models.Model):
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "answer_comments"
        verbose_name = "답변 내용"


class AnswerImages(models.Model):
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE, related_name="images")
    img_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "answer_images"
        verbose_name = "답변 이미지"
