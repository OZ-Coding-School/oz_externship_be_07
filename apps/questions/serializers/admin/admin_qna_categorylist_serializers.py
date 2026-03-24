# apps/questions/serializers/admin/admin_qna_categorylist_serializers.py
from typing import Any, List

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.questions.models import QuestionCategories


# 어드민 카테고리 목록 조회
class AdminQnaCategoryListSerializer(serializers.ModelSerializer): # type: ignore[type-arg]
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
        ]
        ref_name = "AdminQnaCategoryListResponse"

    @extend_schema_field(OpenApiTypes.STR)
    def get_category_type(self, obj: QuestionCategories) -> str:
        if not obj.parent:
            return "large"
        if not obj.parent.parent:
            return "medium"
        return "small"

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_child_categories(self, obj: QuestionCategories) -> List[str]:
        return list(obj.children.all().values_list("name", flat=True))
