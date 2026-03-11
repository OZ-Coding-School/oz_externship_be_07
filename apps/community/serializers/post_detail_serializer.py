from typing import Any

from rest_framework import serializers


class PostDetailAuthorSerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 상세 작성자 Serializer"""

    id = serializers.IntegerField()
    nickname = serializers.CharField()
    profile_img_url = serializers.CharField()


class PostDetailCategorySerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 상세 카테고리 Serializer"""

    id = serializers.IntegerField()
    name = serializers.CharField()


class PostDetailSerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 상세 조회용 Serializer"""

    id = serializers.IntegerField()
    title = serializers.CharField()
    author = PostDetailAuthorSerializer()
    category = PostDetailCategorySerializer()
    content = serializers.CharField()
    view_count = serializers.IntegerField()
    like_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
