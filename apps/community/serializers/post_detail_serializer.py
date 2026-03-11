from typing import Any

from rest_framework import serializers


class PostDetailSerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 상세 조회용 Serializer"""

    id = serializers.IntegerField()
    title = serializers.CharField()
    author = serializers.DictField()
    category = serializers.DictField()
    content = serializers.CharField()
    image_urls = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    comments = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    view_count = serializers.IntegerField()
    like_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
