from django.db import models


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    tag = models.CharField(max_length=3, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OperationManager(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "user_id"], name="uniq_opmgr_course_user"),
        ]


class LearningCoach(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "user_id"], name="uniq_lcoach_course_user"),
        ]


class Subject(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    number_of_days = models.SmallIntegerField(null=True, blank=True)
    number_of_hours = models.SmallIntegerField(null=True, blank=True)
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "title"], name="uniq_subject_course_title"),
        ]


class Cohort(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey("subjects.Course", on_delete=models.CASCADE)
    number = models.SmallIntegerField()
    max_student = models.SmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, default="READY")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "number"], name="uniq_cohort_course_number"),
        ]


class CohortStudent(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cohort", "user_id"], name="uniq_cohort_student_user"),
        ]


class EnrollmentRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    user_id = models.BigIntegerField()
    status = models.CharField(max_length=10, default="PENDING")
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cohort", "user_id"], name="uniq_enrollreq_cohort_user"),
        ]


class TrainingAssistant(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cohort", "user_id"], name="uniq_ta_cohort_user"),
        ]
