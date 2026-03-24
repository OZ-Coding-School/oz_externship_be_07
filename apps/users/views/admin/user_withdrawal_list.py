from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsStaffUser
from apps.users.serializers.admin.user_withdrawal_list import (
    AdminUserWithdrawalListSerializer,
)
from apps.users.services.admin.user_withdrawal import restore_withdrawn_user_by_admin
from apps.users.services.admin.user_withdrawal_list import (
    get_admin_withdrawal_detail_service,
    get_withdrawal_list_service,
)


class AdminUserWithdrawalAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    def get(self, request: Request, withdrawal_id: int | None = None) -> Response:
        """
        탈퇴 목록 조회 또는 특정 탈퇴 정보 상세 조회
        """
        if withdrawal_id is not None:
            try:
                withdrawal = get_admin_withdrawal_detail_service(withdrawal_id)
                serializer = AdminUserWithdrawalListSerializer(withdrawal)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Http404 as e:
                return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_withdrawal_list_service(
            search=request.query_params.get("search"),
            role=request.query_params.get("role"),
            sort=request.query_params.get("sort", "latest"),
        )
        serializer = AdminUserWithdrawalListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, withdrawal_id: int) -> Response:
        """
        회원 탈퇴 취소 처리
        """
        try:
            restore_withdrawn_user_by_admin(withdrawal_id=withdrawal_id)
            return Response({"error_detail": "회원 탈퇴 취소처리 완료."}, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def handle_exception(self, exc: Exception) -> Response:
        """인증/권한 에러 발생 시 커스텀 키값(error_detail)으로 응답"""
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        if isinstance(exc, PermissionDenied):
            return Response({"error_detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)
