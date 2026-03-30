from typing import Any, Optional

from django.db import transaction
from django.db.models import QuerySet
from rest_framework.exceptions import (
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)

from apps.questions.models import QuestionCategories


class AdminQnaCategoryListService:
    @staticmethod
    def get_category_list(
        user: Any, search_keyword: Optional[str] = None, category_type: Optional[str] = None
    ) -> QuerySet[QuestionCategories]:
        if not user or not user.is_authenticated:
            raise NotAuthenticated({"error_detail": "로그인이 필요합니다."})

        if not user.is_staff:
            raise PermissionDenied({"error_detail": "카테고리 목록 조회 권한이 없습니다."})

        queryset = QuestionCategories.objects.all().select_related("parent").prefetch_related("children")

        if category_type:
            if category_type not in ["large", "medium", "small"]:
                raise ValidationError({"error_detail": "유효하지 않은 목록 조회 요청입니다."})

            if category_type == "large":
                queryset = queryset.filter(parent__isnull=True)
            elif category_type == "medium":
                queryset = queryset.filter(parent__isnull=False, parent__parent__isnull=True)
            elif category_type == "small":
                queryset = queryset.filter(parent__parent__isnull=False)

        if search_keyword:
            queryset = queryset.filter(name__icontains=search_keyword.strip())

        return queryset.order_by("-created_at")

    @staticmethod
    @transaction.atomic
    def create_category(user: Any, data: dict[str, Any]) -> QuestionCategories:
        if not user or not user.is_authenticated:
            raise NotAuthenticated({"error_detail": "로그인이 필요합니다."})
        if not user.is_staff:
            raise PermissionDenied({"error_detail": "카테고리 등록 권한이 없습니다."})

        name = data.get("name")
        if not name:
            raise ValidationError({"error_detail": "카테고리 종류와 이름은 필수 입력값입니다."})

        parent_id = data.get("parent_id")
        parent = None
        if parent_id:
            try:
                parent = QuestionCategories.objects.get(id=parent_id)
            except QuestionCategories.DoesNotExist:
                raise NotFound({"error_detail": "상위 카테고리를 찾을 수 없습니다."})

        if QuestionCategories.objects.filter(name=name, parent=parent).exists():
            raise ValidationError({"error_detail": "이미 존재하는 카테고리 이름입니다."})

        return QuestionCategories.objects.create(name=name, parent=parent)
