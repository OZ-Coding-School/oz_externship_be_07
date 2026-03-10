from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class PostListAPIView(APIView):
    """게시글 목록 조회 API"""

    def get(self, request):
        # spec API 단계에서는 mock pagination 응답 반환
        mock_response = {
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
        }
        return Response(mock_response, status=status.HTTP_200_OK)