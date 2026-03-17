from typing import Any

from django.db import transaction
from rest_framework import serializers

from apps.community.models.comment_model import CommentTag, PostComment


class PostCommentSerializer(serializers.ModelSerializer["PostComment"]):
    nickname = serializers.ReadOnlyField(source="author.nickname")

    class Meta:
        model = PostComment
        fields = ["id", "post", "author", "nickname", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "post", "author", "nickname", "created_at", "updated_at"]

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> PostComment:
        post_id = self.context["view"].kwargs.get("post_id")
        author = self.context["request"].user
        content = validated_data.get("content")

        if not content or content == "":
            raise serializers.ValidationError({"content": "이 필드는 필수 항목입니다."})

        try:
            comment = PostComment.objects.create(
                post_id=post_id,
                author=author,
                content=content,
            )

            tagged_ids = self.context["request"].data.get("tagged_user_ids", [])
            for tagged_id in set(tagged_ids):
                CommentTag.objects.create(comment=comment, tagged_user_id=tagged_id)

            return comment

        except Exception as e:
            raise serializers.ValidationError({"error_detail": f"데이터 저장 중 오류가 발생했습니다: {e}"})


class PostCommentUserSearchSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    nickname = serializers.CharField()
    profile_img_url = serializers.CharField(allow_blank=True, allow_null=True)
