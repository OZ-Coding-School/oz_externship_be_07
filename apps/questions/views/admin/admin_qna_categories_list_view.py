from typing import Any

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.admin.admin_qna_categorylist_serializers import (
    AdminQnaCategoryListSerializer,
)
from apps.questions.services.admin.questions_admin_categorylist_services import (
    AdminQnaCategoryListService,
)


class AdminCategoryListAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="어드민 카테고리 등록 API",
        description="새로운 질문 카테고리를 등록합니다.",
        responses={
            201: AdminQnaCategoryListSerializer,
            400: OpenApiResponse(
                description="Bad Request",
                examples=[OpenApiExample("400", value={"error_detail": "카테고리 종류와 이름은 필수 입력값입니다."})],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[OpenApiExample("401", value={"error_detail": "로그인이 필요합니다."})],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[OpenApiExample("403", value={"error_detail": "카테고리 등록 권한이 없습니다."})],
            ),
            404: OpenApiResponse(
                description="Not Found",
                examples=[OpenApiExample("404", value={"error_detail": "상위 카테고리를 찾을 수 없습니다."})],
            ),
            409: OpenApiResponse(
                description="Conflict",
                examples=[OpenApiExample("409", value={"error_detail": "이미 존재하는 카테고리 이름입니다."})],
            ),
        },
        tags=["Admin_qna"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        service = AdminQnaCategoryListService()
        result = service.create_category(user=request.user, data=request.data)

        serializer = AdminQnaCategoryListSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="어드민 카테고리 목록 조회 API",
        parameters=[
            OpenApiParameter(name="search_keyword", description="검색어", type=str),
            OpenApiParameter(name="category_type", description="분류(large, medium, small)", type=str),
        ],
        responses={
            200: AdminQnaCategoryListSerializer(many=True),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[OpenApiExample("400", value={"error_detail": "유효하지 않은 목록 조회 요청입니다."})],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[OpenApiExample("401", value={"error_detail": "로그인이 필요합니다."})],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[OpenApiExample("403", value={"error_detail": "카테고리 목록 조회 권한이 없습니다."})],
            ),
        },
        tags=["Admin_qna"],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        search_keyword = request.query_params.get("search_keyword")
        category_type = request.query_params.get("category_type")

        service = AdminQnaCategoryListService()
        queryset = service.get_category_list(
            user=request.user, search_keyword=search_keyword, category_type=category_type
        )

        serializer = AdminQnaCategoryListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
