from typing import Any

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from apps.questions.models import QuestionCategories


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Success Response Example",
            value={
                "category_id": 55,
                "name": "FastAPI",
                "category_type": "small",
                "parent_id": 12,
                "created_at": "2025-03-03 14:11:22",
            },
            response_only=True,
        )
    ]
)
class AdminCategorySerializer(serializers.ModelSerializer[QuestionCategories]):
    category_id = serializers.IntegerField(source="id", read_only=True)

    category_type = serializers.ChoiceField(
        choices=["large", "medium", "small"], help_text="카테고리 종류 (대분류, 중분류, 소분류)", write_only=True
    )

    parent_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="부모 카테고리 ID",
    )
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = QuestionCategories
        fields = ["category_id", "name", "category_type", "parent_id", "created_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        category_type = attrs.get("category_type")
        parent_id = attrs.get("parent_id")

        if category_type in ["medium", "small"] and not parent_id:
            raise serializers.ValidationError(
                {"parent_id": f"{category_type} 카테고리는 부모 카테고리 설정이 필요합니다."}
            )

        if category_type == "large":
            attrs["parent_id"] = None

        return attrs

    def to_representation(self, instance: QuestionCategories) -> dict[str, Any]:
        ret = super().to_representation(instance)
        ret["parent_id"] = instance.parent.id if instance.parent else None
        return ret
