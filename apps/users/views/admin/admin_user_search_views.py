from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser

from apps.users.choices import UserRole, UserStatus
from apps.users.models.models import User
from apps.users.serializers.admin.admin_user_search_serializers import (
    AdminUserSearchDetailSerializer,
    AdminUserSearchListSerializer,
)
from apps.users.services.admin.admin_user_search_services import AdminUserSearchService


@extend_schema(
    summary="어드민 - 회원 목록 조회",
    tags=["Admin_accounts"],
    description="회원 목록을 조회하고 이름/이메일 검색 및 상태/역할 필터링을 제공합니다.",
    parameters=[
        OpenApiParameter(name="search", description="이름 또는 이메일 검색", required=False, type=str),
        OpenApiParameter(
            name="status", description="회원 상태 필터", required=False, enum=[s.value for s in UserStatus]  # type: ignore
        ),
        OpenApiParameter(name="role", description="회원 권한 필터", required=False, enum=[r.value for r in UserRole]),  # type: ignore
    ],
    responses={
        200: AdminUserSearchListSerializer(many=True),
        401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
    },
)
class AdminUserSearchListView(ListAPIView[User]):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSearchListSerializer

    def get_queryset(self) -> QuerySet["User"]:
        service = AdminUserSearchService()
        return service.get_user_list(
            search=self.request.query_params.get("search"),
            status=self.request.query_params.get("status"),
            role=self.request.query_params.get("role"),
        )


@extend_schema(
    summary="어드민 - 회원 상세 조회",
    tags=["Admin_accounts"],
    description="특정 회원의 상세 정보와 수강 기록을 조회합니다.",
    responses={
        200: AdminUserSearchDetailSerializer,
        401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
        404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
    },
)
class AdminUserSearchDetailView(RetrieveAPIView[User]):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSearchDetailSerializer
    lookup_field = "id"
    lookup_url_kwarg = "account_id"

    def get_object(self) -> "User":
        account_id = self.kwargs.get(self.lookup_url_kwarg)
        service = AdminUserSearchService()
        user = service.get_user_detail(account_id)

        if not user:
            from django.http import Http404

            raise Http404("사용자 정보를 찾을 수 없습니다.")

        return user
