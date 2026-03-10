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


class PostSerializer(serializers.ModelSerializer[Post]):
    images = PostImageSerializer(many=True, read_only=True)
    attachments = PostAttachmentsSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "content", "category", "images", "attachments"]
