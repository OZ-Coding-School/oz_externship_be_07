from typing import Any

from rest_framework import serializers

from apps.community.models.comment_model import PostComment
from apps.users.models.models import User


class CommentAuthorSerializer(serializers.ModelSerializer):
    nickname = serializers.ReadOnlyField()
    profile_img_url = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_img_url"]

class PostCommentSerializer(serializers.ModelSerializer["PostComment"]):
    author = CommentAuthorSerializer(read_only=True)

    class Meta:
        model = PostComment
        fields = ["id", "post", "author", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "post", "author", "created_at", "updated_at"]


class PostCommentUserSearchSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    nickname = serializers.CharField()
    profile_img_url = serializers.CharField(allow_blank=True, allow_null=True)
