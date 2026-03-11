from django.urls import path

from apps.exam import views

urlpatterns = [
    path("admin/exams", views.ExamListCreateAPIView.as_view(), name="exam-list-create"),
    path("admin/exams/<int:exam_id>", views.ExamDetailAPIView.as_view(), name="exam-detail"),
    path(
        "admin/exams/deployments/", views.ExamDeploymentListCreateAPIView.as_view(), name="exam-deployment-list-create"
    ),
    path(
        "admin/exams/deployments/<int:pk>/", views.ExamDeploymentDetailAPIView.as_view(), name="exam-deployment-detail"
    ),
    path(
        "admin/exams/deployments/<int:pk>/status/",
        views.ExamDeploymentStatusUpdateAPIView.as_view(),
        name="exam-deployment-status",
    ),
    path("admin/exams/submissions", views.ExamSubmissionListAPIView.as_view(), name="exam-detail"),
    path(
        "admin/exams/submissions/<int:submission_id>", views.ExamSubmissionDetailAPIView.as_view(), name="exam-detail"
    ),
]
