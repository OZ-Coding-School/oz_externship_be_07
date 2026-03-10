from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.community.models.post_model import Post, PostLike


class PostLikeAPIView(APIView):
    """게시글 좋아요 API"""

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        post_like, created = PostLike.objects.get_or_create(
            user=user,
            post=post
        )

        if not created:
            post_like.is_liked = not post_like.is_liked
            post_like.save()

        like_count = PostLike.objects.filter(
            post=post,
            is_liked=True
        ).count()

        return Response(
            {
                "is_liked": post_like.is_liked,
                "like_count": like_count
            },
            status=status.HTTP_200_OK
        )