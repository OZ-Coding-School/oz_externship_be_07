from rest_framework import serializers

from apps.users.models import User

from .models import QuestionCategories, QuestionImages, Questions


class AuthorSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "nickname", "profile_img_url"]


# 카테고리 시리얼라이저 (질문 등록시 선택)
class CategorySerializer(serializers.ModelSerializer[QuestionCategories]):
    depth = serializers.SerializerMethodField()
    names = serializers.ReadOnlyField(source="name")

    class Meta:
        model = QuestionCategories
        fields = ["id", "depth", "names"]

    def get_depth(self, obj: QuestionCategories) -> int:
        return 1 if obj.parent is None else 2


# 질문 이미지 시리얼라이저
class QuestionImagesSerializer(serializers.ModelSerializer[QuestionImages]):
    class Meta:
        model = QuestionImages
        fields = ["id", "img_url"]


# 목록 조회용: 가볍게
class QuestionListSerializer(serializers.ModelSerializer[Questions]):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Questions
        fields = ["id", "author", "category", "title", "content", "view_count", "created_at"]


# 목록 조회용: 모든 정보가 나오게
class QuestionDetailSerializer(serializers.ModelSerializer[Questions]):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = QuestionImagesSerializer(read_only=True, many=True)

    class Meta:
        model = Questions
        fields = ["id", "author", "category", "images", "title", "content", "view_count", "created_at", "updated_at"]


# 등록용: 입력받을 필드만 입력
class QuestionCreateSerializer(serializers.ModelSerializer[Questions]):
    images = QuestionImagesSerializer(required=False, many=True)

    class Meta:
        model = Questions
        fields = ["category", "title", "content", "images"]

    # 글자 수 유효성 검사
    def validate_title(self, value: str) -> str:
        if len(value) < 3:
            raise serializers.ValidationError("제목은 최소 3글자 이상으로 입력해주세요.")
        return value

    def validate_content(self, value: str) -> str:
        if len(value) < 5:
            raise serializers.ValidationError("내용을 조금 더 길게 작성해주시길 바랍니다.(최소5글자 이상)")
        return value


class QuestionUpdateSerializer(serializers.ModelSerializer[Questions]):
    images = QuestionImagesSerializer(required=False, many=True)

    class Meta:
        model = Questions
        fields = ["category", "title", "content", "images"]

    # 글자 수 유효성 검사
    def validate_title(self, value: str) -> str:
        if len(value) < 3:
            raise serializers.ValidationError("제목은 최소 3글자 이상으로 입력해주세요.")
        return value

    def validate_content(self, value: str) -> str:
        if len(value) < 5:
            raise serializers.ValidationError("내용을 조금 더 길게 작성해주시길 바랍니다.(최소5글자 이상)")
        return value