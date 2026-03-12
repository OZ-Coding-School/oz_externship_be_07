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
                            "category_id": 1,
                        }
                    ],
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

        queryset = get_post_list_queryset(
            search=search,
            search_filter=search_filter,
            category_id=category_id,
            sort=sort,
        )
        values_queryset = get_post_list_values(queryset)

        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)

        if search:
            if search_filter == "author":
                queryset = queryset.filter(author__nickname__icontains=search)
            elif search_filter == "title":
                queryset = queryset.filter(title__icontains=search)
            elif search_filter == "content":
                queryset = queryset.filter(content__icontains=search)
            else:
                queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))

        queryset_any = cast(Any, queryset)
        if sort == "oldest":
            queryset = queryset_any.order_by("created_at", "id")
        elif sort == "most_views":
            queryset = queryset_any.order_by("-view_count", "-id")
        elif sort == "most_likes":
            queryset = queryset_any.order_by("-like_count", "-id")
        elif sort == "most_comments":
            queryset = queryset_any.order_by("-comment_count", "-id")
        else:
            queryset = queryset_any.order_by("-created_at", "-id")

        values_queryset = queryset.values(
            "id",
            "title",
            "content",
            "view_count",
            "created_at",
            "updated_at",
            "category_id",
            "author_id",
            "author__nickname",
            "author__profile_img_url",
            "like_count",
            "comment_count",
            "thumbnail_img_url",
        )

        paginator = PostListPagination()
        page = paginator.paginate_queryset(values_queryset, request)

        page_items: list[dict[str, Any]]
        if page is None:
            page_items = list(values_queryset)
        else:
            page_items = cast(list[dict[str, Any]], page)

        response_data: list[dict[str, Any]] = [
            {
                "id": post["id"],
                "author": {
                    "id": post["author_id"],
                    "nickname": post["author__nickname"],
                    "profile_img_url": post["author__profile_img_url"],
                },
                "title": post["title"],
                "thumbnail_img_url": post["thumbnail_img_url"],
                "content_preview": (f"{post['content'][:50]}..." if len(post["content"]) > 50 else post["content"]),
                "comment_count": post["comment_count"],
                "view_count": post["view_count"],
                "like_count": post["like_count"],
                "created_at": post["created_at"],
                "updated_at": post["updated_at"],
                "category_id": post["category_id"],
            }
            for post in page_items
        ]

        response_data = build_post_list_response(page_items)
        serializer = PostListSerializer(cast(Any, response_data), many=True)

        if page is not None:
            return paginator.get_paginated_response(serializer.data)

        return Response(
            {
                "count": len(serializer.data),
                "next": None,
                "previous": None,
                "results": serializer.data,
            }
        )
