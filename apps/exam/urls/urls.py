from django.urls import path

from apps.exam.views import (
    exam_submission_views,
    exam_views,
)

urlpatterns = [
    ###################### EXAM ##################################
    path("admin/exams", exam_views.ExamListCreateAPIView.as_view(), name="exam-list-create"),
    path("admin/exams/<int:exam_id>", exam_views.ExamDetailAPIView.as_view(), name="exam-detail"),
    ###################### EXAM_SUBMISSION ##########################
    path("admin/exams/submissions", exam_submission_views.ExamSubmissionListAPIView.as_view(), name="exam-submission"),
    path(
        "admin/exams/submissions/<int:submission_id>",
        exam_submission_views.ExamSubmissionDetailAPIView.as_view(),
        name="exam-submission-detail",
    ),
]
