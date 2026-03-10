from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.community.models.post_model import Post
from apps.community.serializers.post_detail_serializer import PostDetailSerializer


class PostDetailAPIView(APIView):
    """게시글 상세 조회 API"""

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostDetailSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)