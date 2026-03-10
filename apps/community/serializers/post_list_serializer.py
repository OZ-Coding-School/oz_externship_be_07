from rest_framework import serializers

from apps.community.models.post_model import Post


class PostListSerializer(serializers.ModelSerializer):
    """게시글 목록 조회용 Serializer"""

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author",
            "created_at",
            "view_count",
            "category",
        ]