from django.urls import path

from apps.exam.views.exam_admin_submission_views import ExamAdminSubmissionListAPIView, ExamAdminSubmissionDetailAPIView

urlpatterns = [
    path("admin/exams/submissions", ExamAdminSubmissionListAPIView.as_view(), name="exam-submission-admin-list"),
    path("admin/exams/submissions/<int:submission_id>", ExamAdminSubmissionDetailAPIView.as_view(), name="exam-submission-admin-detail"),
]
