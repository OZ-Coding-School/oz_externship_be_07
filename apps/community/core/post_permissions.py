from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class PostPermission(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."})

        return True
