from typing import Any

from django.db.models import Prefetch, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.subject.models import CohortStudent
from apps.users.choices import UserRole
from apps.users.models.models import User
from apps.users.serializers.admin.user_search import StudentManagerSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


@extend_schema(tags=["admin_accounts"])
class StudentManagementViewSet(viewsets.ReadOnlyModelViewSet[User]):
    permission_classes = [permissions.IsAdminUser]
    pagination_class = StandardResultsSetPagination
    serializer_class = StudentManagerSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "role"]
    search_fields = ["email", "name", "nickname", "phone_number"]
    ordering_fields = ["id", "name", "birthday"]

    def get_queryset(self) -> QuerySet[User]:
        prefetch_payload = Prefetch(
            "cohortstudent_set", queryset=CohortStudent.objects.select_related("cohort__course").order_by("id")
        )
        return User.objects.exclude(role=UserRole.ADMIN).prefetch_related(prefetch_payload).order_by("id")

    @extend_schema(
        summary="관리자용 학생 목록 조회",
        description="관리자가 학생들의 정보와 현재 수강 중인 기수/코스 데이터를 목록으로 조회합니다.",
        responses={200: StudentManagerSerializer},
    )
    def list(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
