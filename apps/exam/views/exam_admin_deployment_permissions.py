from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

STAFF_ROLES = {"TA", "OM", "LC", "ADMIN"}


class BaseAdminExamDeploymentPermission(permissions.BasePermission):
    message = "권한이 없습니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return getattr(request.user, "role", None) in STAFF_ROLES


class CanCreateExamDeployment(BaseAdminExamDeploymentPermission):
    message = "쪽지시험 배포 생성 권한이 없습니다."


class CanListExamDeployment(BaseAdminExamDeploymentPermission):
    message = "쪽지시험 배포 목록 조회 권한이 없습니다."


class CanDetailExamDeployment(BaseAdminExamDeploymentPermission):
    message = "쪽지시험 배포 상세 조회 권한이 없습니다."


class CanUpdateExamDeployment(BaseAdminExamDeploymentPermission):
    message = "쪽지시험 배포 수정 권한이 없습니다."


class CanUpdateExamDeploymentStatus(BaseAdminExamDeploymentPermission):
    message = "쪽지시험 배포 상태 변경 권한이 없습니다."


class CanDeleteExamDeployment(BaseAdminExamDeploymentPermission):
    message = "배포 삭제 권한이 없습니다."
