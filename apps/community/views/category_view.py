from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models.category_model import PostCategory
from apps.community.serializers.category_serializer import (
    PostCategoryListSpecSerializer,
)


class PostCategoryListSpecAPIView(APIView):
    serializer_class = PostCategoryListSpecSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="v1_posts_category_list",
        tags=["Posts"],
        summary="게시글 카테고리 목록 조회 API",
        description=(
            "커뮤니티 게시글 작성 시 선택 가능한 카테고리 목록을 조회합니다. "
            "활성 카테고리 DB 조회 데이터를 serializer로 직렬화하여 "
            "명세와 동일한 응답 구조(id, name)를 제공합니다."
        ),
        responses={200: PostCategoryListSpecSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="success",
                value=[
                    {"id": 1, "name": "공지사항"},
                    {"id": 2, "name": "자유 게시판"},
                    {"id": 3, "name": "일상 공유"},
                    {"id": 4, "name": "개발 지식 공유"},
                    {"id": 5, "name": "취업 정보 공유"},
                    {"id": 6, "name": "프로젝트 구인"},
                ],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request: Request) -> Response:
        categories = PostCategory.objects.filter(status=True).order_by("id").only("id", "name")
        serializer = self.serializer_class(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
