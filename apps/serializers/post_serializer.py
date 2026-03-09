from rest_framework import serializers
from apps.community.models import Post


class PostCreateSerializer(serializers.ModelSerializer):
    """게시글 작성용 Serializer"""

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "category",
        ]


class PostListSerializer(serializers.ModelSerializer):
    """게시글 목록 조회용 Serializer"""

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "view_count",
            "author",
            "category",
            "created_at",
            "updated_at",
        ]