from typing import Any

from rest_framework import serializers

from apps.users.models import User

from .models import QuestionCategories, QuestionImages, Questions


class AuthorSerializer(serializers.ModelSerializer[User]):
    profile_image_url = serializers.ImageField(source="profile_img_url", read_only=True)

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url"]


# 카테고리 시리얼라이저 (질문 등록시 선택)
class CategorySerializer(serializers.ModelSerializer[QuestionCategories]):
    depth = serializers.SerializerMethodField()
    names = serializers.ReadOnlyField()

    class Meta:
        model = QuestionCategories
        fields = ["id", "depth", "names"]

    def get_depth(self, obj: QuestionCategories) -> int:
        return 1 if obj.parent is None else 2

    def get_names(self, obj: QuestionCategories) -> list[str]:
        result: list[str] = []
        current: QuestionCategories | None = obj
        while current:
            result.insert(0, current.name)
            current = current.parent
        return result


# 질문 이미지 시리얼라이저
class QuestionImagesSerializer(serializers.ModelSerializer[QuestionImages]):
    class Meta:
        model = QuestionImages
        fields = ["id", "img_url"]


# 목록 조회용: 가볍게
class QuestionListSerializer(serializers.ModelSerializer[Questions]):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    content_preview = serializers.SerializerMethodField()
    answer_count = serializers.IntegerField(read_only=True)
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

    def get_thumbnail_img_url(self, obj: Questions) -> str | None:
        first_image = obj.images.first()
        return first_image.img_url if first_image else None


# 목록 조회용: 모든 정보가 나오게
class QuestionDetailSerializer(serializers.ModelSerializer[Questions]):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = QuestionImagesSerializer(read_only=True, many=True)
    # answer_serializers.py 작성되면 여기에 연결!
    # answers = AnswerSerializers(many=True, read_only=True) <- answer_serializers.py 작성되면 주석 해제 serializer 이름 확인하기

    class Meta:
        model = Questions
        fields = [
            "id",
            "title",
            "content",
            "category",
            "images",
            "view_count",
            "author",
            "created_at",  # "answers"
        ]

    # def get_answers(self, obj: Questions) -> list:
    #     answer_serializers와 합쳐질 예정
    #     return []


# 등록용
class QuestionCreateSerializer(serializers.ModelSerializer[Questions]):
    category = serializers.PrimaryKeyRelatedField(queryset=QuestionCategories.objects.all())
    image_url = serializers.ListField(child=serializers.URLField(), write_only=True, required=False)

    class Meta:
        model = Questions
        fields = ["category", "title", "content", "image_url"]

    def create(self, validated_data: dict[str, Any]) -> Questions:
        image_urls = validated_data.pop("image_url", [])
        questions = Questions.objects.create(**validated_data)

        for url in image_urls:
            QuestionImages.objects.create(questions=questions, img_url=url)

        return questions


# 수정용
class QuestionUpdateSerializer(serializers.ModelSerializer[Questions]):
    category = serializers.PrimaryKeyRelatedField(queryset=QuestionCategories.objects.all())
    image_url = serializers.ListField(child=serializers.URLField(), write_only=True, required=False)

    class Meta:
        model = Questions
        fields = ["category", "title", "content", "image_url"]

    def update(self, instance: Questions, validated_data: dict[str, Any]) -> Questions:
        image_urls = validated_data.pop("image_url", None)
        instance = super().update(instance, validated_data)

        if image_urls is not None:
            instance.images.all().delete()
            for url in image_urls:
                QuestionImages.objects.create(questions=instance, img_url=url)

        return instance
