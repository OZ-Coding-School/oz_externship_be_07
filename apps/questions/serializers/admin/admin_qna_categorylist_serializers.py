from typing import Any, List

from rest_framework import serializers

from apps.questions.models import QuestionCategories


class AdminQnaCategoryListSerializer(serializers.ModelSerializer[QuestionCategories]):
    category_id = serializers.IntegerField(source="id", read_only=True)
    category_type = serializers.SerializerMethodField()
    parent_category = serializers.CharField(source="parent.name", read_only=True, default=None)
    child_categories = serializers.SerializerMethodField()

    class Meta:
        model = QuestionCategories
        fields = [
            "category_id",
            "name",
            "category_type",
            "parent_category",
            "child_categories",
            "created_at",
            "updated_at",
        ]
        ref_name = "AdminQnaCategoryListResponse"

    def get_category_type(self, obj: QuestionCategories) -> str:
        if not obj.parent:
            return "large"
        if not obj.parent.parent:
            return "medium"
        return "small"

    def get_child_categories(self, obj: QuestionCategories) -> List[str]:
        return list(obj.children.all().values_list("name", flat=True))

    def create(self, validated_data: dict[str, Any]) -> QuestionCategories:
        instance = super().create(validated_data)
        if not isinstance(instance, QuestionCategories):
            raise TypeError("Expected QuestionCategories instance")
        return instance
