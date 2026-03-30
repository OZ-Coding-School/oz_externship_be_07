from typing import Any, Dict, List

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, NotFound

from apps.questions.models import QuestionCategories


class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = {"error_detail": "동일한 이름의 카테고리가 이미 존재합니다."}
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
    category_type = serializers.ChoiceField(choices=["large", "medium", "small"], write_only=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True)
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
        c_type, p_id = attrs.get("category_type"), attrs.get("parent_id")

        if p_id and not QuestionCategories.objects.filter(id=p_id).exists():
            raise NotFound(detail={"error_detail": "부모 카테고리를 찾을 수 없습니다."})

        if c_type in ["medium", "small"] and not p_id:
            raise serializers.ValidationError({"parent_id": f"{c_type} 카테고리는 부모 설정이 필요합니다."})
        return attrs

    def to_representation(self, instance: QuestionCategories) -> dict[str, Any]:
        ret = super().to_representation(instance)
        p = instance.parent
        ret["parent_id"] = p.id if p else None
        ret["category_type"] = "large" if not p else ("medium" if not p.parent else "small")
        return ret
