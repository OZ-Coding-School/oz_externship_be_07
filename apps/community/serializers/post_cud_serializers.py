from typing import Any

from rest_framework import serializers

from apps.community.models import PostCategory
from apps.community.models.post_model import Post, PostAttachment, PostImage


class PostImageSerializer(serializers.ModelSerializer[PostImage]):
    class Meta:
        model = PostImage
        fields = ["id", "img_url"]


class PostAttachmentsSerializer(serializers.ModelSerializer[PostAttachment]):
    class Meta:
        model = PostAttachment
        fields = ["id", "file_name", "file_url"]


class PostCreateSerializer(serializers.ModelSerializer[Post]):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset = PostCategory.objects.all(),
        source = "category"
    )
    class Meta:
        model = Post
        fields = ["title", "content", "category_id"]

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        title = data.get("title")
        content = data.get("content")
        category = data.get("category")

        errors = {}

        if not title:
            errors["title"] = ["제목은 필수 값입니다."]
        if not content:
            errors["content"] = ["내용은 필수 값입니다."]
        if not category:
            errors["category_id"] = ["카테고리는 필수 값입니다."]

        if errors:
            raise serializers.ValidationError(errors)
        return data


class PostExSerializer(serializers.ModelSerializer[Post]):
    class Meta:
        model = Post
        fields = ["title", "content", "category_id"]


class PostUpdateSerializer(serializers.ModelSerializer[Post]):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset = PostCategory.objects.all(),
        source = "category"
    )

    class Meta:
        model = Post
        fields = ["title", "content", "category_id"]

    def to_representation(self, instance: Post) -> dict[str, Any]:
        return {
            "id": instance.pk,
            "title": instance.title,
            "content": instance.content,
            "category_name": instance.category.name,
        }

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        title = data.get("title")
        content = data.get("content")
        category = data.get("category")

        errors = {}

        if not title:
            errors["title"] = ["제목은 필수 값입니다."]
        if not content:
            errors["content"] = ["내용은 필수 값입니다."]
        if not category:
            errors["category_id"] = ["카테고리는 필수 값입니다."]

        if errors:
            raise serializers.ValidationError(errors)
        return data
