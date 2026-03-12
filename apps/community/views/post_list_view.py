from typing import Any, cast

from django.db.models import Count, OuterRef, Q, Subquery
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models.post_model import Post, PostImage
from apps.community.serializers.post_list_serializer import PostListSerializer


class PostListPagination(PageNumberPagination):
    """게시글 목록 페이지네이션"""

    page_size = 10
    page_size_query_param = "page_size"
    page_query_param = "page"
    max_page_size = 100


class PostListResponseSerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 목록 응답 Serializer"""

    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = PostListSerializer(many=True)


class PostListAPIView(APIView):
    """게시글 목록 조회 API"""

    serializer_class = PostCreateSerializer

    @extend_schema(
        summary="게시글 조회",
        description="게시글 list",
        tags=["posts"],
        parameters=[
            OpenApiParameter(
                name="page",
                description="페이지 번호",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="page_size",
                description="페이지 크기",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="search",
                description="검색어",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="search_filter",
                description="검색 기준",
                required=False,
                type=str,
                enum=["author", "title", "content", "title_or_content"],
            ),
            OpenApiParameter(
                name="category_id",
                description="카테고리 ID",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="sort",
                description="정렬 기준",
                required=False,
                type=str,
                enum=["latest", "oldest", "most_views", "most_likes", "most_comments"],
            ),
        ],
        responses={200: PostListResponseSerializer},
        examples=[
            OpenApiExample(
                name="게시글 조회 예시",
                value={
                    "id": 1,
                    "author": {
                        "id": 1,
                        "nickname": "testuser",
                        "profile_img_url": "https://example.com/uploads/images/users/profiles/image.png",
                    },
                    "title": "테스트 게시글 1번",
                    "thumbnail_img_url": "https://example.com/uploads/images/posts/first-image.png",
                    "content_preview": "그냥 작성한 게시글 1번 입니다. 게시글 본문 내용이 50글자 내로 생략된 형태로 제공됩니다.",
                    "comment_count": 100,
                    "view_count": 100,
                    "like_count": 100,
                    "created_at": "2025-10-30T14:01:57.505250+09:00",
                    "updated_at": "2025-10-30T14:01:57.505250+09:00",
                    "category_id": 1,
                },
                response_only=True,
            )
        ],
    )
    def get(self, request: Request) -> Response:
        search = (request.query_params.get("search") or "").strip()
        search_filter = (request.query_params.get("search_filter") or "").strip()
        sort = (request.query_params.get("sort") or "latest").strip()

        category_id_param = request.query_params.get("category_id")
        category_id: int | None = None
        if category_id_param and category_id_param.isdigit():
            category_id = int(category_id_param)

        thumbnail_subquery = PostImage.objects.filter(post_id=OuterRef("pk")).order_by("id").values("img_url")[:1]

        queryset = (
            Post.objects.select_related("author", "category")
            .filter(is_visible=True, category__status=True)
            .annotate(
                like_count=Count(
                    "likes",
                    filter=Q(likes__is_liked=True),
                    distinct=True,
                ),
                comment_count=Count("postcomment", distinct=True),
                thumbnail_img_url=Subquery(thumbnail_subquery),
            )
        )

    def get(self: "PostListAPIView", request: Request) -> Response:
        search = request.query_params.get("search")
        search_filter = request.query_params.get("search_filter")
        category_id = request.query_params.get("category_id")
        sort = request.query_params.get("sort")
        page = request.query_params.get("page")
        page_size = request.query_params.get("page_size")

        post = Post.objects.select_related("author", "category").first()

        mock_response: dict[str, Any] = {
            "count": 100,
            "next": "http://api.ozcoding.site/api/v1/posts?page=2&page_size=10",
            "previous": "http://api.ozcoding.site/api/v1/posts?page=1&page_size=10",
            "results": [
                {
                    "id": post.id if post else 1,
                    "author": {
                        "id": post.author_id if post else 1,
                        "nickname": post.author.nickname if post else "testuser",
                        "profile_img_url": (
                            post.author.profile_img_url
                            if post and post.author.profile_img_url
                            else "https://example.com/uploads/images/users/profiles/image.png"
                        ),
                    },
                    "title": "테스트 게시글 1번",
                    "thumbnail_img_url": "https://example.com/uploads/images/posts/first-image.png",
                    "content_preview": "그냥 작성한 게시글 1번 입니다. 게시글 본문 내용이 50글자 내로 생략된 형태로 제공됩니다.",
                    "comment_count": 100,
                    "view_count": 100,
                    "like_count": 100,
                    "created_at": "2025-10-30T14:01:57.505250+09:00",
                    "updated_at": "2025-10-30T14:01:57.505250+09:00",
                    "category_id": post.category_id if post else 1,
                }
            ],
        }

        serializer = PostListSerializer(mock_response["results"], many=True)

        return Response(
            {
                "count": mock_response["count"],
                "next": mock_response["next"],
                "previous": mock_response["previous"],
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
