from django.http import Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsStaffUser
from apps.users.services.admin.user_withdrawal import restore_withdrawn_user_by_admin


class AdminUserWithdrawalRestoreAPIView(APIView):
    """
    어드민 페이지에서 탈퇴한 회원의 계정을 복구(탈퇴 취소)하는 API입니다.
    """

    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        summary="어드민 페이지 탈퇴 취소 API",
        tags=["Admin_accounts"],
        responses={
            200: OpenApiResponse(description="회원 탈퇴 취소처리 완료."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="회원탈퇴 정보를 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, withdrawal_id: int) -> Response:
        try:
            restore_withdrawn_user_by_admin(withdrawal_id=withdrawal_id)
            return Response({"detail": "회원 탈퇴 취소처리 완료."}, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        if isinstance(exc, PermissionDenied):
            return Response({"error_detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)
