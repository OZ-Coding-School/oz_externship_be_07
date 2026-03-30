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

from apps.questions.serializers.admin.admin_qna_categoryserializers import (
    AdminCategorySerializer,
)
from apps.questions.services.admin.questions_admin_categorylist_services import (
    AdminQnaCategoryListService,
)


class AdminCategoryListAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="관리자 카테고리 목록 조회",
        description="관리자용 질문 카테고리 목록을 조회합니다. 대/중/소 분류 필터링 및 키워드 검색을 지원합니다.",
        parameters=[
            OpenApiParameter(name="page", description="페이지 번호", type=int, default=1),
            OpenApiParameter(name="size", description="페이지당 항목 수", type=int, default=20),
            OpenApiParameter(name="search_keyword", description="카테고리명 검색어", type=str),
            OpenApiParameter(name="category_type", description="카테고리 분류 (large, medium, small)", type=str),
        ],
        responses={
            200: AdminCategorySerializer(many=True),  # 실제 응답 구조에 맞게 페이징 시리얼라이저가 있다면 교체 필요
            400: OpenApiResponse(
                description="잘못된 요청",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 요청 예시",
                        value={"error_detail": "유효하지 않은 목록 조회 요청입니다."},
                    )
                ],
            ),
            401: OpenApiResponse(
                description="인증 실패",
                examples=[
                    OpenApiExample(
                        "로그인 필요 예시",
                        value={"error_detail": "로그인이 필요합니다."},
                    )
                ],
            ),
            403: OpenApiResponse(
                description="권한 없음",
                examples=[
                    OpenApiExample(
                        "권한 부족 예시",
                        value={"error_detail": "카테고리 목록 조회 권한이 없습니다."},
                    )
                ],
            ),
        },
        tags=["Admin_qna"],
    )
    def get(self, request: Request) -> Response:
        search_keyword = request.query_params.get("search_keyword")
        category_type = request.query_params.get("category_type")

        queryset = AdminQnaCategoryListService.get_category_list(
            user=request.user,
            search_keyword=search_keyword,
            category_type=category_type,
        )

        serializer = AdminCategorySerializer(queryset, many=True)

        return Response(
            {
                "page": int(request.query_params.get("page", 1)),
                "size": int(request.query_params.get("size", 20)),
                "total_count": queryset.count(),
                "categories": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
