from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.users.models import User
from apps.users.serializers.admin_user_search_serializers import (
    StudentManagerSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지 크기
    max_page_size = 100  # 최대 페이지 크기


class StudentManagementViewSet(viewsets.ReadOnlyModelViewSet[User]):

    # 페이지네이션 설정
    pagination_class = StandardResultsSetPagination

    # ID 순으로 기본 정렬
    queryset = User.objects.all().order_by("id")

    serializer_class = StudentManagerSerializer
    # 기능 확장: 필터링, 검색, 정렬 백엔드
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # 필터링 (과정, 기수, 상태 등)
    filterset_fields = ["status", "role"]
    # 검색 (이메일, 이름, 닉네임, 연락처)
    search_fields = ["email", "name", "nickname", "phone_number"]
    # 정렬 (기본값 외에 추가 허용할 항목)
    ordering_fields = ["id", "name", "birthday"]

    @extend_schema(
        summary="관리자용 학생 목록 조회",
        description="관리자가 학생들의 정보와 현재 수강 중인 기수/코스 데이터를 목록으로 조회합니다.",
        tags=["Admin - User Management"],
        examples=[
            OpenApiExample(
                name="학생 목록 조회 성공 예시",
                description="페이지네이션이 적용된 학생 목록 데이터입니다.",
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "email": "test@example.com",
                            "nickname": "코딩왕김오즈",
                            "name": "김오즈",
                            "phone_number": "010-1234-5678",
                            "birthday": "1998-08-29",
                            "status": "activated",
                            "role": "student",
                            "in_progress_course": {
                                "cohort": {"id": 1, "number": 10},
                                "course": {"id": 1, "name": "백엔드 초격차 부트캠프", "tag": "BE"},
                            },
                            "created_at": "2026-03-11T14:00:00Z",
                        }
                    ],
                },
                response_only=True,
            )
        ],
        responses={
            200: StudentManagerSerializer,
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="관리자 권한이 없습니다."),
        },
    )
    def list(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
