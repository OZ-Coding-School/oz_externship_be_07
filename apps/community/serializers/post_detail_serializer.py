from rest_framework import serializers
from apps.community.models.post_model import Post


class PostDetailSerializer(serializers.ModelSerializer):
    """게시글 상세 조회용 Serializer"""

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author",
            "created_at",
            "updated_at",
            "view_count",
            "category",
        ]