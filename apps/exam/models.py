from django.db import models

from apps.core.models import TimeStampModel
from apps.exam.choices import DeploymentStatus, QuestionType
from apps.subject.models import Cohort, Subject
from apps.users.models import User

# Create your models here.


class Exam(TimeStampModel):
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    thumbnail_img_url = models.CharField(max_length=255, default="default_img_url")

    class Meta:
        db_table = "exams"


# 10. 시험 문제 (exam_questions)
class ExamQuestion(TimeStampModel):
    exam_id = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    prompt = models.TextField(null=True, blank=True)
    blank_count = models.SmallIntegerField(null=True, blank=True)
    options_json = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=20, choices=QuestionType)
    answer = models.JSONField()
    point = models.SmallIntegerField()
    explanation = models.TextField()

    class Meta:
        db_table = "exam_questions"


# 11. 시험 배포 관리 (TimeStampModel)
class ExamDeployment(TimeStampModel):
    cohort_id = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    exam_id = models.ForeignKey(Exam, on_delete=models.CASCADE)
    duration_time = models.SmallIntegerField(default=60)
    access_code = models.CharField(max_length=64)
    open_at = models.DateTimeField()
    close_at = models.DateTimeField()
    questions_snapshot_json = models.JSONField()
    status = models.CharField(max_length=20, default="Activated", choices=DeploymentStatus)

    class Meta:
        db_table = "exam_deployments"


# 12. 시험 완료 정보 (TimeStampModel)
class ExamSubmission(TimeStampModel):
    submitter_id = models.ForeignKey(User, on_delete=models.CASCADE)
    deployment_id = models.ForeignKey(ExamDeployment, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    cheating_count = models.SmallIntegerField()
    answers_json = models.JSONField()
    score = models.SmallIntegerField()
    correct_answer_count = models.SmallIntegerField()

    class Meta:
        db_table = "exam_submissions"
