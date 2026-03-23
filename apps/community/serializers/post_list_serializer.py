from typing import Any

from rest_framework import serializers

from apps.community.services.post_service import RE_IMAGE_URL, presigned_url_change


class PostListAuthorSerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 목록 작성자 Serializer"""

    id = serializers.IntegerField()
    nickname = serializers.CharField()
    profile_img_url = serializers.CharField(allow_null=True)


class PostListSerializer(serializers.Serializer[dict[str, Any]]):
    """게시글 목록 조회용 Serializer"""

    id = serializers.IntegerField()
    author = PostListAuthorSerializer()
    title = serializers.CharField()
    thumbnail_img_url = serializers.SerializerMethodField()
    content_preview = serializers.CharField()
    comment_count = serializers.IntegerField()
    view_count = serializers.IntegerField()
    like_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    category_name = serializers.CharField()

    def get_thumbnail_img_url(self, obj: dict[str, Any]) -> str | None:
        content = obj.get("content")
        if not content:
            return None

        img_urls = RE_IMAGE_URL.findall(content)
        for img_url in img_urls:
            return presigned_url_change(img_url.split("com/")[1])

        return None
