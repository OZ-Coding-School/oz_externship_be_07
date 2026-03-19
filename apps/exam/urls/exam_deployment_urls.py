from django.urls import path

from apps.exam.views.exam_deployment_access_views import DeploymentCheckCodeAPIView
from apps.exam.views.exam_deployment_views import (
    DeploymentDetailAPIView,
    DeploymentListAPIView,
    DeploymentStatusAPIView,
)

urlpatterns = [
    path("api/v1/exams/deployments", DeploymentListAPIView.as_view()),
    path("api/v1/exams/deployments/<int:deployment_id>/check-code", DeploymentCheckCodeAPIView.as_view()),
    path("api/v1/exams/deployments/<int:deployment_id>", DeploymentDetailAPIView.as_view()),
    path("api/v1/exams/deployments/<int:deployment_id>/status", DeploymentStatusAPIView.as_view()),
]
