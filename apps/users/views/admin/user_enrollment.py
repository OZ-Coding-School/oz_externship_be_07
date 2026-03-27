from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsStaffUser
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.serializers.admin.user_enrollment import AdminUserEnrollmentSerializer


@extend_schema_view(
    list=extend_schema(summary="관리자용 수강생 등록 요청 목록 조회 API", tags=["Admin_accounts"]),
    retrieve=extend_schema(summary="관리자용 수강생 등록 요청 목록 상세조회 API", tags=["Admin_accounts"]),
)
class AdminUserEnrollmentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet[EnrollmentRequest]
):
    """
    권한: 운영진(TA, OM, LC, ADMIN) 전용 API
    """

    queryset = EnrollmentRequest.objects.select_related("user", "cohort", "cohort__course").all()
    serializer_class = AdminUserEnrollmentSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # 필터/검색 필드 설정
    filterset_fields = ["status"]
    search_fields = ["user__name", "user__email"]
    ordering = ["-created_at"]
