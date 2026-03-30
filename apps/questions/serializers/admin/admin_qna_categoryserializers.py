from typing import Any, Dict, List

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, NotFound

from apps.questions.models import QuestionCategories


class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "이미 존재하는 카테고리 이름입니다."
    default_code = "conflict"


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

    name = serializers.CharField(max_length=100, validators=[], help_text="카테고리 이름")

    category_type = serializers.ChoiceField(
        choices=["large", "medium", "small"],
        help_text="카테고리 종류 (대분류, 중분류, 소분류)",
        write_only=True,
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

        validators: List[Any] = []

        extra_kwargs: Dict[str, Any] = {"name": {"validators": []}}

    def validate_name(self, value: str) -> str:
        if QuestionCategories.objects.filter(name=value).exists():
            raise ConflictException()
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        category_type = attrs.get("category_type")
        parent_id = attrs.get("parent_id")

        if parent_id:
            if not QuestionCategories.objects.filter(id=parent_id).exists():
                raise NotFound(detail=f"ID {parent_id}인 부모 카테고리를 찾을 수 없습니다.")

        if category_type in ["medium", "small"] and not parent_id:
            raise serializers.ValidationError(
                {"parent_id": f"{category_type} 카테고리는 부모 카테고리 설정이 필요합니다."}
            )

        if category_type == "large":
            attrs["parent_id"] = None

        return attrs

    def create(self, validated_data: dict[str, Any]) -> QuestionCategories:
        parent_id = validated_data.pop("parent_id", None)
        if parent_id:
            validated_data["parent"] = QuestionCategories.objects.get(id=parent_id)

        instance = super().create(validated_data)
        if not isinstance(instance, QuestionCategories):
            raise TypeError("생성된 객체가 QuestionCategories 인스턴스가 아닙니다.")
        return instance

    def to_representation(self, instance: QuestionCategories) -> dict[str, Any]:
        ret = super().to_representation(instance)
        ret["parent_id"] = instance.parent.id if instance.parent else None

        if instance.parent is None:
            ret["category_type"] = "large"
        elif instance.parent.parent is None:
            ret["category_type"] = "medium"
        else:
            ret["category_type"] = "small"

        return ret
