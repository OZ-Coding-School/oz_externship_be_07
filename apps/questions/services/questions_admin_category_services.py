from typing import Any, Dict

from rest_framework.exceptions import NotFound, ValidationError

from apps.questions.models import QuestionCategories


class AdminCategoryService:
    @staticmethod
    def create_category(data: Dict[str, Any]) -> QuestionCategories:
        name = data.get("name")
        category_type = data.get("category_type")
        parent_id = data.get("parent_id")

        # 1. 필수값 체크 (Error 400)
        if not name or not category_type:
            raise ValidationError("카테고리 종류와 이름은 필수입니다.")

        # 2. 부모 카테고리 존재 여부 체크 (Error 404)
        if parent_id and not QuestionCategories.objects.filter(id=parent_id).exists():
            raise NotFound("부모 카테고리를 찾을 수 없습니다.")

        # 3. 중복 이름 체크 (Error 409)
        if QuestionCategories.objects.filter(name=name).exists():
            raise ValidationError("동일한 이름의 카테고리가 이미 존재합니다.")

        # 4. 데이터 생성
        return QuestionCategories.objects.create(name=name, parent_id=parent_id)
