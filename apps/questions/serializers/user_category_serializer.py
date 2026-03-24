from typing import Any

from rest_framework import serializers

from apps.questions.models import QuestionCategories
from apps.questions.services.user_categories_list_services import QuestionCategoryService


class UserCategorySerializer(serializers.ModelSerializer[QuestionCategories]):
    category_type = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = QuestionCategories
        fields = ["id", "name", "category_type", "children"]

    def get_category_type(self, obj: QuestionCategories) -> str:
        return QuestionCategoryService.get_category_type(obj)

    def get_children(self, obj: QuestionCategories) -> Any:
        children = obj.children.all()
        if children.exists():
            return UserCategorySerializer(children, many=True).data
        return []
