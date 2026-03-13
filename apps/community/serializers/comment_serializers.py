from rest_framework import serializers

from apps.community.models.comment_model import PostComment


class PostCommentSerializer(serializers.ModelSerializer["PostComment"]):
    author_name = serializers.ReadOnlyField(source="author.nickname")

    class Meta:
        model = PostComment
        fields = ["id", "post", "author", "author_name", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "post", "author", "author_name", "created_at", "updated_at"]
