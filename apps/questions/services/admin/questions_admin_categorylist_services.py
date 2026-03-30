from typing import Any, Optional

from django.db.models import QuerySet
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)

from ...models import QuestionCategories


# 카테고리 목록 조회
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
            valid_types = ["large", "medium", "small"]
            if category_type not in valid_types:
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
