from rest_framework import serializers

from apps.questions.models import QuestionCategories


# admin 카테고리 등록 시리얼라이저
class AdminCategoryCreateSerializer(serializers.ModelSerializer[QuestionCategories]):
    category_id = serializers.IntegerField(source="id", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = QuestionCategories
        fields = [
            "category_id",
            "name",
            "category_type",
            "parent_id",
            "created_at",
        ]

