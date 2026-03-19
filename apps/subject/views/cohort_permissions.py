from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

STAFF_ROLES = {"TA", "OM", "LC", "ADMIN"}


class IsSubjectStaffUser(permissions.BasePermission):
    message = "권한이 없습니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user and request.user.is_authenticated and getattr(request.user, "role", None) in STAFF_ROLES
        )


class CanViewCohortList(permissions.BasePermission):
    message = "이 리소스를 조회할 권한이 없습니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user and request.user.is_authenticated and getattr(request.user, "role", None) in STAFF_ROLES
        )
