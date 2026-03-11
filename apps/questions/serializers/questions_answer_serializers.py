from rest_framework import serializers

from .common_serializers import AuthorSerializer
from ..models import AnswerImages, AnswerComments, Answers


class AnswerImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerImages
        fields = ["id", "img_url"]

class AnswerCommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = AnswerComments
        fields = ["id", "author", "content", "created_at"]

class AnswersSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    comments = AnswerCommentSerializer(many=True, read_only=True)
    images = AnswerImagesSerializer(many=True, read_only=True)

    image_urls = serializers.ListField(
        child=serializers.URLField(), write_only=True, required=False
    )

    class Meta:
        model = Answers
        fields = [
            "id", "author", "content", "is_adopted",
            "images", "image_urls", "comments", "created_at"
        ]
        read_only_fields = ["is_adopted"]