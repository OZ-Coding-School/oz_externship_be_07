from typing import Any

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers import PostUpdateSerializer
from apps.community.serializers.post_detail_serializer import PostDetailSerializer
from apps.community.services.post_service import (
    build_post_detail_response,
    get_post_detail,
)


class PostDetailNotFoundSerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 상세 조회 실패 응답 Serializer"""

    error_detail = serializers.CharField()


class PostDetailAPIView(APIView):
    """게시글 상세 조회 API"""

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
