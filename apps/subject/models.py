from django.db import models

from apps.core.models import TimeStampModel
from apps.subject.choices import CohortStatus, StudentEnrollmentRequestsStatus
from apps.users.models import User

# Create your models here.


# 1. 수업 과정 (courses)
class Course(TimeStampModel):
    name = models.CharField(max_length=30, unique=True)
    tag = models.CharField(max_length=3, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "courses"


# 2. 운영 매니저 (operation_managers)
class OperationManager(TimeStampModel):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "operation_managers"


# 3. 러닝 코치 (learning_coachs)
class LearningCoach(TimeStampModel):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "learning_coachs"


# 4. 기수 (cohorts)
class Cohort(TimeStampModel):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    number = models.SmallIntegerField()
    max_student = models.SmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, default="PENDING", choices=CohortStatus)

    class Meta:
        db_table = "cohorts"
        indexes = [
            models.Index(fields=["course_id", "number"]),
        ]


# 5. 기수 학생 (cohort_students)
class CohortStudent(TimeStampModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    cohort_id = models.ForeignKey(Cohort, on_delete=models.CASCADE)

    class Meta:
        db_table = "cohort_students"


# 6. 학생 등록 요청 (student_enrollment_requests)
class EnrollmentRequest(TimeStampModel):
    cohort_id = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default="PENDING", choices=StudentEnrollmentRequestsStatus)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "enrollment_requests"


# 7. 트레이닝 어시스턴트 (training_assistants)
class TrainingAssistant(TimeStampModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    cohort_id = models.ForeignKey(Cohort, on_delete=models.CASCADE)

    class Meta:
        db_table = "training_assistants"


# 8. 과목 (subjects)
class Subject(TimeStampModel):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=30, unique=True)
    number_of_days = models.SmallIntegerField()
    number_of_hours = models.SmallIntegerField()
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "subjects"
        indexes = [
            models.Index(fields=["course_id", "title"]),
        ]
