from typing import cast

from django.http import Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models.post_model import Post
from apps.community.serializers.post_like_serializer import PostLikeResponseSerializer
from apps.community.services.post_like_service import set_post_like


class PostLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Posts"],
        summary="게시글 좋아요",
        responses={
            200: PostLikeResponseSerializer,
            404: OpenApiResponse(description="게시글을 찾을 수 없습니다."),
        },
    )
    def post(self, request: Request, post_id: int) -> Response:
        try:
            dto = set_post_like(
                post_id=post_id,
                user_id=cast(int, request.user.id),
                is_liked=True,
            )
        except Post.DoesNotExist as exc:
            raise Http404 from exc

        serializer = PostLikeResponseSerializer(dto)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Posts"],
        summary="게시글 좋아요 취소",
        responses={
            200: PostLikeResponseSerializer,
            404: OpenApiResponse(description="게시글을 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, post_id: int) -> Response:
        try:
            dto = set_post_like(
                post_id=post_id,
                user_id=cast(int, request.user.id),
                is_liked=False,
            )
        except Post.DoesNotExist as exc:
            raise Http404 from exc

        serializer = PostLikeResponseSerializer(dto)
        return Response(serializer.data, status=status.HTTP_200_OK)
