from django.urls import path

from apps.exam.views.exam_user_submission_views import (
    ExamSubmissionAPIView,
    ExamSubmissionDetailAPIView,
)

urlpatterns = [
    path("exams/submissions", ExamSubmissionAPIView.as_view(), name="exam-submission-create"),
    path("exams/submissions/<submission_id>", ExamSubmissionDetailAPIView.as_view(), name="exam-submission-detail"),
]
