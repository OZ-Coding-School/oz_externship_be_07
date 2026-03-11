from typing import Any

from rest_framework import serializers

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

    class Meta:
        model = Post
        fields = ["title", "content", "category"]

    def to_representation(self, instance: Post) -> dict[str, Any]:
        return {
            "detail": "게시글이 성공적으로 생성되었습니다.",
            "pk": instance.pk,
        }

class PostUpdateSerializer(serializers.ModelSerializer[Post]):

    class Meta:
        model = Post
        fields = ["title", "content", "category"]

    def to_representation(self, instance: Post) -> dict[str, Any]:
        return {
            "id": instance.pk,
            "title": instance.title,
            "content": instance.content,
            "category_id": instance.category.id,
        }

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        title = data.get("title")
        content = data.get("content")
        category_id = data.get("category")

        if not title or not content or category_id is None:
            raise serializers.ValidationError("제목, 내용, 카테고리는 필수 값입니다.")
        return data
