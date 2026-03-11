from typing import Any

from rest_framework import serializers


class PostDetailSerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 상세 조회용 Serializer"""

    id = serializers.IntegerField()
    title = serializers.CharField()
    author = serializers.IntegerField()
    category = serializers.IntegerField()
    content = serializers.CharField()
    view_count = serializers.IntegerField()
    like_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
