from django.urls import path

from apps.exam.views import exam_views, exam_deployment_views, exam_submission_views

urlpatterns = [  ###################### EXAM ##################################
    path("admin/exams", exam_views.ExamListCreateAPIView.as_view(), name="exam-list-create"),
    path("admin/exams/<int:exam_id>", exam_views.ExamDetailAPIView.as_view(), name="exam-detail"),
    ###################### EXAM_DEPLOYMENT ##########################
    path(
        "admin/exams/deployments/",
        exam_deployment_views.ExamDeploymentListCreateAPIView.as_view(),
        name="exam-deployment-list-create",
    ),
    path(
        "admin/exams/deployments/<int:pk>/",
        exam_deployment_views.ExamDeploymentDetailAPIView.as_view(),
        name="exam-deployment-detail",
    ),
    path(
        "admin/exams/deployments/<int:pk>/status/",
        exam_deployment_views.ExamDeploymentStatusUpdateAPIView.as_view(),
        name="exam-deployment-status",
    ),
    ###################### EXAM_SUBMISSION ##########################
    path("admin/exams/submissions", exam_submission_views.ExamSubmissionListAPIView.as_view(), name="exam-detail"),
    path(
        "admin/exams/submissions/<int:submission_id>",
        exam_submission_views.ExamSubmissionDetailAPIView.as_view(),
        name="exam-detail",
    ),
]
