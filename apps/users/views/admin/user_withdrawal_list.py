from django.http import Http404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsStaffUser
from apps.users.serializers.admin.user_withdrawal_list import (
    AdminUserWithdrawalDetailSerializer,
    AdminUserWithdrawalListSerializer,
)
from apps.users.services.admin.user_withdrawal import restore_withdrawn_user_by_admin
from apps.users.services.admin.user_withdrawal_list import (
    get_admin_withdrawal_detail_service,
    get_withdrawal_list_service,
)


class AdminUserWithdrawalAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    pagination_class = PageNumberPagination

    @extend_schema(
        summary="어드민 탈퇴 회원 목록/상세 조회",
        description="withdrawal_id 유무에 따라 상세 조회(DetailSerializer) 또는 페이징된 목록 조회(ListSerializer)를 수행합니다.",
        parameters=[
            OpenApiParameter(name="page", description="페이지 번호", type=int),
            OpenApiParameter(name="search", description="이름 검색", type=str),
            OpenApiParameter(name="role", description="역할 필터", type=str),
            OpenApiParameter(name="sort", description="정렬 (latest/oldest)", type=str),
        ],
        responses={
            200: OpenApiResponse(description="조회 성공"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="회원탈퇴 정보를 찾을 수 없습니다."),
        },
        tags=["Admin_accounts"],
    )
    def get(self, request: Request, withdrawal_id: int | None = None) -> Response:
        if withdrawal_id is not None:
            try:
                withdrawal = get_admin_withdrawal_detail_service(withdrawal_id)
                detail_serializer = AdminUserWithdrawalDetailSerializer(withdrawal)
                return Response(detail_serializer.data, status=status.HTTP_200_OK)
            except Http404 as e:
                return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_withdrawal_list_service(
            search=request.query_params.get("search"),
            role=request.query_params.get("role"),
            sort=request.query_params.get("sort", "latest"),
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is not None:
            list_serializer = AdminUserWithdrawalListSerializer(page, many=True)
            return paginator.get_paginated_response(list_serializer.data)

        list_serializer = AdminUserWithdrawalListSerializer(queryset, many=True)
        return Response(list_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="어드민 탈퇴 회원 복구(탈퇴 취소)",
        description="특정 탈퇴 기록을 삭제하여 유저의 상태를 활성으로 복구합니다.",
        responses={
            200: OpenApiResponse(description="회원 탈퇴 취소처리 완료."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="회원탈퇴 정보를 찾을 수 없습니다."),
        },
        tags=["Admin_accounts"],
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
