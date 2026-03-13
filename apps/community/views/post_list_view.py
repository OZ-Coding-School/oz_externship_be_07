from typing import Any, cast

from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers import PostCreateSerializer
from apps.community.serializers.post_list_serializer import PostListSerializer
from apps.community.services.post_service import (
    build_post_list_response,
    get_post_list_queryset,
    get_post_list_values,
)


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
            OpenApiParameter(name="page", description="페이지 번호", required=False, type=int),
            OpenApiParameter(name="page_size", description="페이지 크기", required=False, type=int),
            OpenApiParameter(name="search", description="검색어", required=False, type=str),
            OpenApiParameter(
                name="search_filter",
                description="검색 기준",
                required=False,
                type=str,
                enum=["author", "title", "content", "title_or_content"],
            ),
            OpenApiParameter(name="category_id", description="카테고리 ID", required=False, type=int),
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
                    "count": 100,
                    "next": "http://api.ozcoding.site/api/v1/posts?page=2&page_size=10",
                    "previous": None,
                    "results": [
                        {
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
                            "category_name": "자유게시판",
                        }
                    ],
                },
                response_only=True,
            )
        ],
    )
    def get(self, request: Request) -> Response:
        category_id_param = request.query_params.get("category_id")
        queryset = get_post_list_queryset(
            search=(request.query_params.get("search") or "").strip(),
            search_filter=(request.query_params.get("search_filter") or "").strip(),
            category_id=int(category_id_param) if category_id_param and category_id_param.isdigit() else None,
            sort=(request.query_params.get("sort") or "latest").strip(),
        )
        values_queryset = get_post_list_values(queryset)
        paginator = PostListPagination()
        page = paginator.paginate_queryset(values_queryset, request)
        serializer = PostListSerializer(
            cast(
                Any,
                build_post_list_response(list(values_queryset) if page is None else cast(list[dict[str, Any]], page)),
            ),
            many=True,
        )

        return (
            paginator.get_paginated_response(serializer.data)
            if page is not None
            else Response({"count": len(serializer.data), "next": None, "previous": None, "results": serializer.data})
        )
