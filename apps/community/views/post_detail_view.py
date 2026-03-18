from typing import Any

from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.core.extend_schema import value_list
from apps.community.models.post_model import Post
from apps.community.serializers import PostUpdateSerializer
from apps.community.serializers.post_cud_serializers import PostUpdateSerializer
from apps.community.serializers.post_detail_serializer import PostDetailSerializer
from apps.community.serializers.post_like_serializer import (
    PostLikeRequestSerializer,
    PostLikeResponseSerializer,
)
from apps.community.services.post_like_service import set_post_like
from apps.community.services.post_metric_service import (
    build_post_viewer_key,
    get_merged_post_view_count,
    increase_post_view_count,
)
from apps.community.services.post_service import (
    build_post_detail_response,
    delete_post,
    file_synchronization,
    get_post_detail,
    post_file_delete,
    post_image_delete,
    update_post,
)


class PostDetailNotFoundSerializer(serializers.Serializer[dict[str, Any]]):
    error_detail = serializers.CharField()


class PostDetailAPIView(APIView):
    """게시글 상세 조회 API"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="게시글 상세 조회",
        tags=["posts"],
        responses={
            200: PostDetailSerializer,
            404: PostDetailNotFoundSerializer,
        },
    )
    def get(self, request: Request, post_id: int) -> Response:
        post = get_post_detail(post_id)

        if post is None:
            error_serializer = PostDetailNotFoundSerializer({"error_detail": "게시글을 찾을 수 없습니다."})
            return Response(error_serializer.data, status=status.HTTP_404_NOT_FOUND)

        viewer_key = build_post_viewer_key(request)
        increase_post_view_count(post.id, viewer_key)

        merged_view_count = get_merged_post_view_count(post.id, post.view_count)

        response_data = build_post_detail_response(post)
        response_data["view_count"] = merged_view_count

        response_serializer = PostDetailSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="게시글 좋아요 반영",
        tags=["posts"],
        request=PostLikeRequestSerializer,
        responses={
            200: PostLikeResponseSerializer,
            404: PostDetailNotFoundSerializer,
        },
        examples=[
            OpenApiExample(
                name="좋아요 요청",
                value={"is_liked": True},
            ),
            OpenApiExample(
                name="좋아요 취소 요청",
                value={"is_liked": False},
            ),
        ],
    )
    def post(self, request: Request, post_id: int) -> Response:
        if not request.user.is_authenticated:
            return Response(
                {"detail": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request_serializer = PostLikeRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            post_like_dto = set_post_like(
                post_id=post_id,
                user_id=request.user.id,
                is_liked=request_serializer.validated_data["is_liked"],
            )
        except Post.DoesNotExist:
            error_serializer = PostDetailNotFoundSerializer({"error_detail": "게시글을 찾을 수 없습니다."})
            return Response(error_serializer.data, status=status.HTTP_404_NOT_FOUND)

        response_serializer = PostLikeResponseSerializer(post_like_dto)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["posts"],
        summary="게시판 수정",
        request=PostUpdateSerializer,
        description="커뮤니티 게시글 수정 API",
        examples=[
            value_list["200"],
            value_list["403"],
            value_list["404"],
            value_list["400"],
            value_list["401"],
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def put(self, request: Request, post_id: int) -> Response:
        try:
            instance = get_object_or_404(Post, pk=post_id)
        except Http404:
            return Response({"error_detail": "해당 게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        if instance.author.pk != request.user.pk:
            return Response({"error_detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostUpdateSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        update_post(
            instance,
            serializer.validated_data["title"],
            serializer.validated_data["content"],
            serializer.validated_data["category"],
        )
        file_synchronization(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["posts"],
        summary="게시판 삭제",
        description="커뮤니티 게시글 삭제 API",
        examples=[
            value_list["200_delete"],
            value_list["403"],
            value_list["404"],
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def delete(self, request: Request, post_id: int) -> Response:
        try:
            instance = get_object_or_404(Post, pk=post_id)
        except Http404:
            return Response({"error_detail": "해당 게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        if instance.author.pk != request.user.pk:
            return Response({"error_detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        delete_post(instance)
        post_file_delete(instance)
        post_image_delete(instance)

        return Response({"detail": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
