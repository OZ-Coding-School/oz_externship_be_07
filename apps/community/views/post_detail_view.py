from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers.post_detail_serializer import PostDetailSerializer


class PostDetailAPIView(APIView):
    """게시글 상세 조회 API"""

    def get(self: "PostDetailAPIView", request: Request, post_id: int) -> Response:
        if post_id != 1:
            return Response(
                {"error_detail": "게시글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mock_response: dict[str, Any] = {
            "id": 1,
            "title": "테스트 게시글 1번",
            "author": {
                "id": 1,
                "nickname": "testuser",
                "profile_img_url": "https://example.com/uploads/images/users/profiles/image.png",
            },
            "category": {
                "id": 1,
                "name": "자유",
            },
            "content": "게시글 본문입니다.",
            "image_urls": [
                "https://example.com/uploads/images/posts/first-image.png",
            ],
            "comments": [
                {
                    "author": {
                        "id": 2,
                        "nickname": "comment_user",
                        "profile_img_url": "https://example.com/uploads/images/users/profiles/comment-user.png",
                    },
                    "content": "댓글 내용입니다.",
                    "created_at": "2025-10-30T15:01:57.505250+09:00",
                    "tagged_users": ["testuser"],
                }
            ],
            "view_count": 100,
            "like_count": 100,
            "created_at": "2025-10-30T14:01:57.505250+09:00",
            "updated_at": "2025-10-30T14:01:57.505250+09:00",
        }

        serializer = PostDetailSerializer(mock_response)
        return Response(serializer.data, status=status.HTTP_200_OK)
