from rest_framework import serializers

from ..models import AnswerComments, AnswerImages, Answers
from .common_serializers import AuthorSerializer


# 답변 이미지
class AnswerImagesSerializer(serializers.ModelSerializer[AnswerImages]):
    class Meta:
        model = AnswerImages
        fields = ["id", "img_url"]
        read_only_fields = fields


# 답변 댓글
class AnswerCommentSerializer(serializers.ModelSerializer[AnswerComments]):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = AnswerComments
        fields = ["id", "author", "content", "created_at"]
        read_only_fields = fields


# 답변 댓글 입력
class CommentCreateSerializer(serializers.Serializer[None]):
    content = serializers.CharField(min_length=1, max_length=500)


# 답변 입력 (등록/수정)
class AnswerCreateUpdateSerializer(serializers.ModelSerializer[Answers]):
    image_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=list,
    )

    class Meta:
        model = Answers
        fields = ["content", "image_urls"]


# 답변 상세 (상세 조회용)
class AnswerResponseSerializer(serializers.ModelSerializer[Answers]):
    author = AuthorSerializer(read_only=True)
    images = AnswerImagesSerializer(many=True, read_only=True)
    comments = AnswerCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Answers
        fields = ["id", "author", "content", "is_adopted", "images", "comments", "created_at"]
        read_only_fields = fields


# Presigned URL 요청
class PresignedUrlRequestSerializer(serializers.Serializer[None]):
    file_name = serializers.CharField()
