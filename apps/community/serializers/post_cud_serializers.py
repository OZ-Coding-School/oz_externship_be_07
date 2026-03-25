from typing import Any

from rest_framework import serializers

from apps.community.core.constants import EXTRA_KWARGS
from apps.community.models.category_model import PostCategory
from apps.community.models.post_model import Post, PostAttachment, PostImage


class PostImageSerializer(serializers.ModelSerializer[PostImage]):
    """이미지 파일 저장 Serializer"""

    class Meta:
        model = PostImage
        fields = ["id", "img_url"]


class PostAttachmentsSerializer(serializers.ModelSerializer[PostAttachment]):
    """첨부 파일 저장 Serializer"""

    class Meta:
        model = PostAttachment
        fields = ["id", "file_name", "file_url"]


class PostCreateSerializer(serializers.ModelSerializer[Post]):
    """게시글 저장 Serializer"""

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=PostCategory.objects.filter(status=True),
        source="category",
        error_messages={"null": "카테고리는 필수 값입니다."},
    )

    class Meta:
        model = Post
        fields = ["title", "content", "category_id"]
        extra_kwargs = EXTRA_KWARGS


class PostUpdateSerializer(serializers.ModelSerializer[Post]):
    """게시글 수정 Serializer"""

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=PostCategory.objects.filter(status=True),
        source="category",
        error_messages={"null": "카테고리는 필수 값입니다."},
    )

    class Meta:
        model = Post
        fields = ["title", "content", "category_id"]
        extra_kwargs = EXTRA_KWARGS

    def to_representation(self, instance: Post) -> dict[str, Any]:
        return {
            "id": instance.pk,
            "title": instance.title,
            "content": instance.content,
            "category_name": instance.category.name,
        }
