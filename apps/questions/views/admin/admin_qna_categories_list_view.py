from typing import Any, cast

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.admin.admin_qna_categorylist_serializers import (
    AdminQnaCategoryListSerializer,
)
from apps.questions.serializers.admin.admin_qna_categoryserializers import (
    AdminCategorySerializer,
)
from apps.questions.services.admin.questions_admin_category_services import (
    AdminCategoryService,
)
from apps.questions.services.admin.questions_admin_categorylist_services import (
    AdminQnaCategoryListService,
)


class AdminCategoryPagination(PageNumberPagination):
    page_size_query_param = "size"
    max_page_size = 100

    def get_paginated_response(self, data: Any) -> Response:
        request = self.request
        if request is None:
            return Response({"success": False, "Message": "Request is Missing"}, status=400)

        current_page = int(request.query_params.get(self.page_query_param, 1))
        current_size = int(request.query_params.get(self.page_size_query_param, str(self.page_size)))

        total_count = self.page.paginator.count if self.page else 0

        return Response(
            {
                "page": current_page,
                "size": current_size,
                "total_count": total_count,
                "categories": data,
            }
        )


class AdminCategoryAPIView(APIView):
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

        return Response(
            {"categories": serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="관리자 카테고리 등록",
        request=AdminCategorySerializer,
        responses={201: AdminCategorySerializer},
        tags=["Admin - Questions"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AdminCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category = AdminCategoryService.create_category(validated_data=serializer.validated_data)

        response_serializer = AdminCategorySerializer(category)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
