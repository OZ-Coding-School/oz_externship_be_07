from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import PostCategory
from apps.community.serializers import PostCategoryListSpecSerializer


class PostCategoryListSpecAPIView(APIView):
    """
    커뮤니티 게시글 카테고리 목록 조회 (SPEC 전용)

    - DB 데이터와 무관하게 항상 같은 응답 구조 제공
    - 응답스키마(id, name)를 기준으로 화면/API연동 진행바람.

    HTTP Method:
        GET /api/v1/posts/categories
    """

    serializer_class = PostCategoryListSpecSerializer
    permission_classes = [AllowAny]  # SPEC단계 인증없이 문서/연동 확인

    def _build_mock_categories(self) -> list[PostCategory]:
        """
        DB 조회없이 모델 인스턴스 직접 생성
        -> 프론트는 아래 응답 형태만 기준으로 연동하면 됨.
        """
        return [
            PostCategory(id=1, name="공지사항"),
            PostCategory(id=2, name="자유 게시판"),
            PostCategory(id=3, name="일상 공유"),
            PostCategory(id=4, name="개발 지식 공유"),
            PostCategory(id=5, name="취업 정보 공유"),
            PostCategory(id=6, name="프로젝트 구인"),
        ]

    @extend_schema(
        operation_id="v1_posts_category_list",
        tags=["커뮤니티 관리"],
        summary="커뮤니티 게시글 카테고리 목록 조회 API",
        description=(
            "커뮤니티 게시글 작성 시 선택 가능한 카테고리 목록을 조회합니다. "
            "Spec 단계에서는 DB 조회 없이 모델 mock 데이터를 serializer로 직렬화하여 "
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
        # mock 데이터 -> serializer -> 실제 API와 동일한 JSON 구조 반환
        categories = self._build_mock_categories()
        serializer = self.serializer_class(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
