from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

STAFF_ROLES = {"TA", "OM", "LC", "ADMIN"}


class IsStaffUser(permissions.BasePermission):
    """유저의 role이 운영진(TA, OM, LC, ADMIN)인 경우에만 접근 허용"""

    message = "권한이 없습니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user and request.user.is_authenticated and getattr(request.user, "role", None) in STAFF_ROLES
        )
