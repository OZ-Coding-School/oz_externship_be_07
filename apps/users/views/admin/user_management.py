from django.http import Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.core.permissions import IsSelfOrReadOnly
from apps.users.choices import UserRole
from apps.users.services.admin.user_management import delete_user_by_admin


class AdminUserDeleteAPIView(APIView):
    """
    관리자 페이지에서 사용자를 삭제하는 API입니다.
    """

    permission_classes = [IsSelfOrReadOnly]

    def check_permissions(self, request: Request) -> None:
        super().check_permissions(request)

        user_role = getattr(request.user, "role", None)
        is_manager = user_role in [
            UserRole.TA,
            UserRole.OM,
            UserRole.ADMIN,
            UserRole.LC,
        ]

        if not is_manager:
            raise PermissionDenied()

    @extend_schema(
        summary="어드민 페이지 사용자 삭제 API",
        tags=["admin_accounts"],
        responses={
            200: OpenApiResponse(description="유저 데이터가 삭제되었습니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, account_id: int) -> Response:
        try:
            deleted_pk = delete_user_by_admin(account_id=account_id)
            return Response({"detail": f"유저 데이터가 삭제되었습니다. - pk: {deleted_pk}"}, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error_detail": "사용자 정보를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

        if isinstance(exc, PermissionDenied):
            return Response({"error_detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        return super().handle_exception(exc)
