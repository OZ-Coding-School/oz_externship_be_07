from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.subject.models import EnrollmentRequest
from apps.users.serializers.admin.user_enrollement import AdminUserEnrollmentSerializer


class IsStaffUser(permissions.BasePermission):
    """
    유저의 role이 운영진(TA, OM, LC, ADMIN)인 경우에만 접근 허용
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        staff_roles = ["TA", "OM", "LC", "ADMIN"]
        return bool(
            request.user and request.user.is_authenticated and getattr(request.user, "role", None) in staff_roles
        )


@extend_schema_view(
    list=extend_schema(summary="관리자용 수강생 등록 요청 목록 조회 API", tags=["admin_enrollments"]),
    retrieve=extend_schema(summary="관리자용 수강생 등록 요청 목록 상세조회 API", tags=["admin_enrollments"]),
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
    ordering = ["-created_at"]
