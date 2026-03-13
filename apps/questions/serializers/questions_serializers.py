from typing import Any, Optional

from rest_framework import serializers

from apps.questions.models import QuestionCategories, QuestionImages, Questions
from apps.questions.serializers.answers_serializers import AnswersSerializer
from apps.questions.serializers.common_serializers import AuthorSerializer


# 카테고리 시리얼라이저 (질문 등록시 선택)
class CategorySerializer(serializers.ModelSerializer[QuestionCategories]):
    depth = serializers.SerializerMethodField()
    names = serializers.SerializerMethodField()

    class Meta:
        model = QuestionCategories
        fields = ["id", "depth", "names"]

    def get_depth(self, obj: QuestionCategories) -> int:
        depth = 0
        current: QuestionCategories | None = obj
        while current:
            depth += 1
            current = current.parent
        return depth

    def get_names(self, obj: QuestionCategories) -> list[str]:
        names: list[str] = []
        current: QuestionCategories | None = obj

        while current:
            names.append(current.name)
            current = current.parent
        return names[::-1]


# 질문 이미지 시리얼라이저
class QuestionImagesSerializer(serializers.ModelSerializer[QuestionImages]):
    class Meta:
        model = QuestionImages
        fields = ["id", "img_url"]


# 목록 조회용: 가볍게
class QuestionListSerializer(serializers.ModelSerializer[Questions]):
    category = CategorySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    content_preview = serializers.SerializerMethodField()
    answer_count = serializers.IntegerField(read_only=True, default=0)
    thumbnail_img_url = serializers.SerializerMethodField()

    class Meta:
        model = Questions
        fields = [
            "id",
            "category",
            "author",
            "title",
            "content_preview",
            "answer_count",
            "view_count",
            "created_at",
            "thumbnail_img_url",
        ]

    def get_content_preview(self, obj: Questions) -> str:
        if obj.content:
            return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
        return ""

    def get_thumbnail_img_url(self, obj: Questions) -> Optional[str]:
        first_image = obj.images.first()
        return first_image.img_url if first_image else None


# 목록 조회용: 모든 정보가 나오게
class QuestionListDetailSerializer(serializers.ModelSerializer[Questions]):
    category = CategorySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    images = QuestionImagesSerializer(read_only=True, many=True)
    answers = AnswersSerializer(read_only=True, many=True)

    class Meta:
        model = Questions
        fields = ["id", "title", "content", "category", "images", "view_count", "created_at", "author", "answers"]


# 등록용
class QuestionCreateSerializer(serializers.Serializer[Any]):
    category_id = serializers.IntegerField(help_text="카테고리_ID")
    title = serializers.CharField(
        max_length=100, min_length=3, error_messages={"min_length": "제목은 최소 3글자 이상이어야 합니다."}
    )
    content = serializers.CharField(min_length=5, error_messages={"min_length": "내용은 최소 5글자 이상이어야 합니다."})
    image_urls = serializers.ListField(child=serializers.URLField(), required=False, default=list)

    def validate_category_id(self, value: int) -> int:
        if not QuestionCategories.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 카테고리 입니다.")
        return value


# 질문 등록 성공 시 응답용
class QuestionCreateResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField(default="질문이 성공적으로 등록되었습니다.")
    question_id = serializers.IntegerField(source="id")


# 수정용
class QuestionUpdateSerializer(serializers.Serializer[Any]):
    category_id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=100, min_length=3, required=False)
    content = serializers.CharField(min_length=5, required=False)
    image_urls = serializers.ListField(child=serializers.URLField(), required=False)

    def validate_category_id(self, value: Optional[int]) -> Optional[int]:
        if value is not None and not QuestionCategories.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 카테고리입니다.")
        return value


# 질문 등록 수정 시 응답용
class QuestionUpdateResponseSerializer(serializers.Serializer[Any]):
    question_id = serializers.IntegerField(source="id")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
