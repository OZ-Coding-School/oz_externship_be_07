from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.community.models.post_model import Post
from apps.community.serializers.post_list_serializer import PostListSerializer


class PostListAPIView(APIView):
    """게시글 목록 조회 API"""

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)