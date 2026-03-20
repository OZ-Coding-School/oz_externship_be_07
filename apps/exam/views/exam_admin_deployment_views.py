from apps.exam.views.exam_admin_deployment_command_views import (
    AdminExamDeploymentCreateAPIView,
    AdminExamDeploymentDeleteAPIView,
    AdminExamDeploymentStatusUpdateAPIView,
    AdminExamDeploymentUpdateAPIView,
)
from apps.exam.views.exam_admin_deployment_query_views import (
    AdminExamDeploymentDetailAPIView,
    AdminExamDeploymentListAPIView,
)


class AdminExamDeploymentListCreateAPIView(
    AdminExamDeploymentCreateAPIView,
    AdminExamDeploymentListAPIView,
):
    pass


class AdminExamDeploymentDetailUpdateDeleteAPIView(
    AdminExamDeploymentDetailAPIView,
    AdminExamDeploymentUpdateAPIView,
    AdminExamDeploymentDeleteAPIView,
):
    pass


class AdminExamDeploymentStatusAPIView(AdminExamDeploymentStatusUpdateAPIView):
    pass
