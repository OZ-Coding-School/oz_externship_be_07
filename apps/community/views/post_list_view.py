from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models.post_model import Post
from apps.community.serializers import PostCreateSerializer
from apps.community.serializers.post_list_serializer import PostListSerializer


class PostListAPIView(APIView):
    """게시글 목록 조회 API"""

    serializer_class = PostCreateSerializer

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

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({"detail": "게시글이 성공적으로 생성되었습니다.", "pk": 1}, status=status.HTTP_201_CREATED)
