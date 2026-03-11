from typing import Any

from rest_framework import serializers

from .models import AnswerComments, AnswerImages, Answers, QuestionAiAnswers
from .questions_serializer import AuthorSerializer


# 1. AI 답변
class QuestionAiAnswerSerializer(serializers.ModelSerializer[QuestionAiAnswers]):
    class Meta:
        model = QuestionAiAnswers
        fields = ["output", "using_model", "created_at"]


# 2. 답변 이미지
class AnswerImagesSerializer(serializers.ModelSerializer[AnswerImages]):
    class Meta:
        model = AnswerImages
        fields = ["id", "img_url"]


# 3. 답변 댓글
class AnswerCommentSerializer(serializers.ModelSerializer[AnswerComments]):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = AnswerComments
        fields = ["id", "author", "content", "created_at"]


# 4. 메인 답변
class AnswersSerializer(serializers.ModelSerializer[Answers]):
    author = AuthorSerializer(read_only=True)
    comments = AnswerCommentSerializer(many=True, read_only=True)
    images = AnswerImagesSerializer(many=True, read_only=True)

    # 팀원 필드명 'image_url'로 통일
    image_url = serializers.ListField(child=serializers.URLField(), write_only=True, required=False)

    class Meta:
        model = Answers
        fields = ["id", "questions", "author", "content", "is_adopted", "comments", "images", "image_url", "created_at"]
        read_only_fields = ["is_adopted"]

    def create(self, validated_data: dict[str, Any]) -> Answers:
        image_urls = validated_data.pop("image_url", [])
        answer = Answers.objects.create(**validated_data)
        for url in image_urls:
            AnswerImages.objects.create(answer=answer, img_url=url)
        return answer

    def update(self, instance: Answers, validated_data: dict[str, Any]) -> Answers:
        image_urls = validated_data.pop("image_url", None)
        instance = super().update(instance, validated_data)
        # 협의된 정책: 이미지 들어오면 전체 교체
        if image_urls is not None:
            instance.images.all().delete()
            for url in image_urls:
                AnswerImages.objects.create(answer=instance, img_url=url)
        return instance
