from typing import Any

from django.db import transaction
from rest_framework.exceptions import APIException, NotFound, ValidationError

from apps.questions.models import QuestionCategories


class Conflict(APIException):
    status_code = 409
    default_detail = "이미 존재하는 리소스입니다."
    default_code = "conflict"


class AdminCategoryService:
    @staticmethod
    @transaction.atomic
    def create_category(validated_data: dict[str, Any]) -> QuestionCategories:
        name: str = validated_data.get("name", "").strip()
        category_type: str = validated_data.get("category_type", "").strip()
        parent_id: Any = validated_data.get("parent_id")

        if not name or not category_type:
            raise ValidationError({"error_detail": "카테고리 종류와 이름은 필수 입력값입니다."})

        parent = None
        if parent_id:
            try:
                parent = QuestionCategories.objects.get(id=parent_id)
            except QuestionCategories.DoesNotExist:
                raise NotFound({"error_detail": "부모 카테고리를 찾을 수 없습니다."})

        if QuestionCategories.objects.filter(name=name, parent=parent).exists():
            raise Conflict({"error_detail": "동일한 이름의 카테고리가 이미 존재합니다."})

        # 카테고리 생성
        category = QuestionCategories.objects.create(
            name=name,
            parent=parent,
        )

        return category
