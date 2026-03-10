from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class PostDetailAPIView(APIView):
    """게시글 상세 조회 API"""

    def get(self, request, post_id):
        # spec API 단계에서는 1번 게시글만 존재하는 mock 데이터로 가정
        if post_id != 1:
            return Response(
                {"error_detail": "게시글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mock_response = {
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
            "view_count": 100,
            "like_count": 100,
            "created_at": "2025-10-30T14:01:57.505250+09:00",
            "updated_at": "2025-10-30T14:01:57.505250+09:00",
        }
        return Response(mock_response, status=status.HTTP_200_OK)