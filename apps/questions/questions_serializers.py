from rest_framework import serializers

from .models import QuestionCategories, QuestionImages, Questions


# 카테고리 시리얼라이저 (질문 등록시 선택)
class QuestionCategorySerializer(serializers.ModelSerializer[QuestionCategories]):
    class Meta:
        model = QuestionCategories
        fields = ["id", "name", "parent"]


# 질문 이미지 시리얼라이저
class QuestionImagesSerializer(serializers.ModelSerializer[QuestionImages]):
    class Meta:
        model = QuestionImages
        fields = ["id", "img_url"]


# 질문 등록 및 상세 조회(카테고리) 시리얼라이저
class QuestionsSerializer(serializers.ModelSerializer[Questions]):
    author_nickname = serializers.ReadOnlyField(source="author.nickname")
    view_count = serializers.IntegerField(read_only=True)
    images = QuestionImagesSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d")

    # 카테고리 정보(입력할때는 id를 받지만, 보여줄때는 이름을 보여줄 수 있게 설정)
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Questions
        fields = [
            "id",
            "author_nickname",
            "category",
            "category_name",
            "title",
            "content",
            "view_count",
            "images",
            "created_at",
            "updated_at",
        ]

    # 글자 수 유효성 검사
    def validate_title(self, value: str) -> str:
        if len(value) < 3:
            raise serializers.ValidationError("제목은 최소 3글자 이상으로 입력해주세요.")
        return value

    def validate_content(self, value: str) -> str:
        if len(value) < 5:
            raise serializers.ValidationError("내용을 조금 더 길게 작성해주시길 바랍니다.(최소5글자 이상)")
        return value
