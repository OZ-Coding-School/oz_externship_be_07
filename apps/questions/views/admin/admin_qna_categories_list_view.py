# apps/questions/views/admin/admin_qna_categories_list_views.py
from typing import Any

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# 정확한 파일명으로 임포트 경로 수정
from apps.questions.serializers.admin.admin_qna_categorylist_serializers import (
    AdminQnaCategoryListSerializer,
)
from apps.questions.services.admin.questions_admin_categorylist_services import (
    AdminQnaCategoryListService,
)


class AdminCategoryPagination(PageNumberPagination):
    page_size_query_param = "size"
    max_page_size = 100


# 어드민 카테고리 목록 조회
class AdminCategoryListAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="어드민 카테고리 목록 조회",
        description="카테고리 타입별 필터링 및 이름 검색 기능을 제공합니다.",
        parameters=[
            OpenApiParameter(name="page", description="페이지 번호", type=int, default=1),
            OpenApiParameter(name="size", description="페이지당 항목 수", type=int, default=10),
            OpenApiParameter(name="search_keyword", description="카테고리명 검색어", type=str),
            OpenApiParameter(name="category_type", description="카테고리 타입 (large, medium, small)", type=str),
        ],
        responses={200: AdminQnaCategoryListSerializer(many=True)},
        tags=["Admin - Questions"],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        search_keyword = request.query_params.get("search_keyword")
        category_type = request.query_params.get("category_type")

        queryset = AdminQnaCategoryListService.get_category_list(
            search_keyword=search_keyword, category_type=category_type
        )

        paginator = AdminCategoryPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is not None:
            serializer = AdminQnaCategoryListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AdminQnaCategoryListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
