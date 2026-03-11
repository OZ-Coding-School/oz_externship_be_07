from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models.post_model import Post
from apps.community.serializers.post_detail_serializer import PostDetailSerializer


class PostDetailAPIView(APIView):
    """게시글 상세 조회 API"""

    def get(self: "PostDetailAPIView", request: Request, post_id: int) -> Response:
        post = Post.objects.select_related("author", "category").filter(id=post_id).first()

        if post is None:
            return Response(
                {"error_detail": "게시글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mock_response: dict[str, Any] = {
            "id": post.id,
            "title": "테스트 게시글 1번",
            "author": {
                "id": post.author_id,
                "nickname": post.author.nickname,
                "profile_img_url": (
                    post.author.profile_img_url
                    if post.author.profile_img_url
                    else "https://example.com/uploads/images/users/profiles/image.png"
                ),
            },
            "category": {
                "id": post.category_id,
                "name": post.category.name,
            },
            "content": "게시글 본문입니다.",
            "view_count": 100,
            "like_count": 100,
            "created_at": "2025-10-30T14:01:57.505250+09:00",
            "updated_at": "2025-10-30T14:01:57.505250+09:00",
        }

        serializer = PostDetailSerializer(mock_response)
        return Response(serializer.data, status=status.HTTP_200_OK)
