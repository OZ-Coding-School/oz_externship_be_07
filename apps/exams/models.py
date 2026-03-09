from django.db import models


class Exam(models.Model):
    id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey("subjects.Subject", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    thumbnail_img_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["subject", "title"], name="uniq_exam_subject_title"),
        ]


class ExamQuestion(models.Model):
    id = models.BigAutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    prompt = models.TextField(null=True, blank=True)
    blank_count = models.SmallIntegerField(null=True, blank=True)
    options_json = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=20)
    answer = models.JSONField()
    point = models.SmallIntegerField()
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ExamDeployment(models.Model):
    id = models.BigAutoField(primary_key=True)
    cohort = models.ForeignKey("subjects.Cohort", on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    duration_time = models.SmallIntegerField()
    access_code = models.CharField(max_length=64, unique=True)
    open_at = models.DateTimeField()
    close_at = models.DateTimeField()
    questions_snapshot_json = models.JSONField()
    status = models.CharField(max_length=10, default="READY")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ExamSubmission(models.Model):
    id = models.BigAutoField(primary_key=True)
    submitter_id = models.BigIntegerField()
    deployment = models.ForeignKey(ExamDeployment, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    cheating_count = models.SmallIntegerField()
    answers_json = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["deployment", "submitter_id"], name="uniq_submission_deploy_user"),
        ]
