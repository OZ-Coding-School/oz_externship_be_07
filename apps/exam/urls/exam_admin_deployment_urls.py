from django.urls import path

from apps.exam.views.exam_admin_deployment_views import (
    AdminExamDeploymentDetailUpdateDeleteAPIView,
    AdminExamDeploymentListCreateAPIView,
    AdminExamDeploymentStatusAPIView,
)

urlpatterns = [
    path("admin/exams/deployments", AdminExamDeploymentListCreateAPIView.as_view()),
    path(
        "admin/exams/deployments/<int:deployment_id>",
        AdminExamDeploymentDetailUpdateDeleteAPIView.as_view(),
    ),
    path(
        "admin/exams/deployments/<int:deployment_id>/status",
        AdminExamDeploymentStatusAPIView.as_view(),
    ),
]
