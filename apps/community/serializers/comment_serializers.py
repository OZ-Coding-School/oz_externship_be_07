from typing import Any

from rest_framework import serializers

from apps.community.models.comment_model import PostComment


class PostCommentSerializer(serializers.ModelSerializer["PostComment"]):
    nickname = serializers.ReadOnlyField(source="author.nickname")

    class Meta:
        model = PostComment
        fields = ["id", "post", "author", "nickname", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "post", "author", "nickname", "created_at", "updated_at"]


class PostCommentUserSearchSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    nickname = serializers.CharField()
    profile_img_url = serializers.CharField(allow_blank=True, allow_null=True)
