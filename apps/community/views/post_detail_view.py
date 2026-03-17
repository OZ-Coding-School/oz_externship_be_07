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
from apps.community.serializers import PostUpdateSerializer, PostExSerializer
from apps.community.serializers.post_detail_serializer import PostDetailSerializer
from apps.community.services.post_service import (
    build_post_detail_response,
    delete_post,
    get_post_detail,
    update_post, post_file_upload,
)


class PostDetailNotFoundSerializer(serializers.Serializer[dict[str, str]]):
    """게시글 상세 조회 실패 응답 Serializer"""

    error_detail = serializers.CharField()


class PostDetailAPIView(APIView):
    """게시글 상세 조회 API"""

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostUpdateSerializer

    @extend_schema(
        summary="게시글 상세 조회",
        description="게시글에 대한 상세한 정보 조회",
        tags=["posts"],
        responses={200: PostDetailSerializer, 404: PostDetailNotFoundSerializer},
        examples=[
            OpenApiExample(
                name="게시글 상세 조회 성공 예시",
                value={
                    "id": 1,
                    "title": "테스트 게시글",
                    "author": {
                        "id": 1,
                        "nickname": "testuser",
                        "profile_img_url": "https://example.com/uploads/images/users/profiles/profile.png",
                    },
                    "category": {"id": 1, "name": "자유게시판"},
                    "content": "게시글 내용입니다.",
                    "view_count": 100,
                    "like_count": 10,
                    "created_at": "2025-10-30T14:01:57.505250+09:00",
                    "updated_at": "2025-10-30T14:01:57.505250+09:00",
                },
                response_only=True,
            ),
            OpenApiExample(
                name="게시글 상세 조회 실패 예시",
                value={"error_detail": "게시글을 찾을 수 없습니다."},
                response_only=True,
            ),
        ],
    )
    def get(self, request: Request, post_id: int) -> Response:
        post = get_post_detail(post_id)
        return (
            Response({"error_detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
            if post is None
            else Response(
                PostDetailSerializer(build_post_detail_response(post)).data,
                status=status.HTTP_200_OK,
            )
        )

    @extend_schema(
        tags=["posts"],
        summary="게시판 수정",
        request=PostExSerializer,
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
            data = {"error_detail": "해당 게시글을 찾을 수 없습니다."}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        if instance.author.pk != request.user.pk:
            data = {"error_detail": "권한이 없습니다."}
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        request_data = update_post(instance, serializer.validated_data)
        serializer.instance = request_data

        file = serializer.validated_data.get("markdownimg", None)
        if file:
            post_file_upload(instance, file)

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
            data = {"error_detail": "해당 게시글을 찾을 수 없습니다."}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        if instance.author.pk != request.user.pk:
            data = {"error_detail": "권한이 없습니다."}
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        delete_post(instance)
        data = {"detail": "게시글이 삭제되었습니다."}
        return Response(data, status=status.HTTP_200_OK)
