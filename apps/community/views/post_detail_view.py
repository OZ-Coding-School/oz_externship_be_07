from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.core.extend_schema import value_list
from apps.community.core.permissions import IsSelfOrReadOnly
from apps.community.models.post_model import Post
from apps.community.serializers.post_cud_serializers import PostUpdateSerializer
from apps.community.serializers.post_detail_serializer import PostDetailSerializer
from apps.community.services.post_metric_service import (
    build_post_viewer_key,
    get_merged_post_view_count,
    increase_post_view_count,
)
from apps.community.services.post_service import (
    build_post_detail_response,
    get_post_detail,
    post_delete,
)
from apps.community.tasks import file_synchronization_task, post_file_delete_task


class PostDetailNotFoundSerializer(serializers.Serializer[dict[str, Any]]):
    error_detail = serializers.CharField()


class PostDetailAPIView(APIView):
    permission_classes = [IsSelfOrReadOnly]
    serializer_class = PostUpdateSerializer

    @staticmethod
    def _not_found_response() -> Response:
        serializer = PostDetailNotFoundSerializer({"error_detail": "게시글을 찾을 수 없습니다."})
        return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def _get_visible_post(post_id: int) -> Post:
        try:
            return Post.objects.select_related("author", "category").get(
                id=post_id,
                is_visible=True,
                category__status=True,
            )
        except Post.DoesNotExist as e:
            raise NotFound(detail={"error_detail": "해당 게시글을 찾을 수 없습니다."})

    @extend_schema(
        summary="게시글 상세 조회",
        description="게시글에 대한 상세한 정보 조회",
        tags=["Posts"],
        responses={
            200: PostDetailSerializer,
            404: PostDetailNotFoundSerializer,
        },
        examples=[
            OpenApiExample(
                name="게시글 상세 조회 성공 예시",
                value={
                    "id": 1,
                    "author": {
                        "id": 1,
                        "nickname": "testuser",
                        "profile_img_url": "https://example.com/profile.png",
                    },
                    "category_id": "1",
                    "category_name": "자유게시판",
                    "title": "테스트 게시글",
                    "content": "게시글 내용입니다.",
                    "view_count": 10,
                    "like_count": 3,
                    "created_at": "2026-03-01T12:00:00Z",
                    "updated_at": "2026-03-01T12:00:00Z",
                },
                response_only=True,
            )
        ],
    )
    def get(self, request: Request, post_id: int) -> Response:
        post = get_post_detail(post_id)
        if post is None:
            return self._not_found_response()

        viewer_key = build_post_viewer_key(request)
        increase_post_view_count(post.id, viewer_key)

        response_data = build_post_detail_response(post)
        response_data["view_count"] = get_merged_post_view_count(
            post.id,
            post.view_count,
        )

        serializer = PostDetailSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="게시글 수정",
        description="게시글을 수정합니다.",
        tags=["Posts"],
        request=PostUpdateSerializer,
        examples=[value_list["200"], value_list["400"], value_list["401"], value_list["403"], value_list["404"]],
        responses={
            200: PostDetailSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: PostDetailNotFoundSerializer,
        },
    )
    def put(self, request: Request, post_id: int) -> Response:

        post = self._get_visible_post(post_id)
        self.check_object_permissions(request, post)

        serializer = PostUpdateSerializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        post.refresh_from_db()
        file_synchronization_task(post_id, post.content)

        updated_post = get_post_detail(post_id)
        if updated_post is None:
            return self._not_found_response()

        response_serializer = PostDetailSerializer(build_post_detail_response(updated_post))
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="게시글 삭제",
        description="게시글을 삭제합니다.",
        tags=["Posts"],
        examples=[value_list["200_delete"], value_list["400"], value_list["401"], value_list["403"], value_list["404"]],
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: PostDetailNotFoundSerializer,
        },
    )
    def delete(self, request: Request, post_id: int) -> Response:

        post = self._get_visible_post(post_id)
        self.check_object_permissions(request, post)

        post_file_delete_task(post_id)
        post_delete(post)

        return Response(
            {"detail": "게시글이 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )
