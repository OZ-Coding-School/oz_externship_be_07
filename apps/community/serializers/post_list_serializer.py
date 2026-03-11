from typing import Any

from rest_framework import serializers


class PostListSerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 목록 조회용 Serializer"""

    id = serializers.IntegerField()
    author = serializers.IntegerField()
    title = serializers.CharField()
    thumbnail_img_url = serializers.CharField(allow_null=True)
    content_preview = serializers.CharField()
    comment_count = serializers.IntegerField()
    view_count = serializers.IntegerField()
    like_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    category = serializers.IntegerField()
